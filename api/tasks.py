from celery import shared_task
from openai import OpenAI
from pydantic import ValidationError
import os
import json
import time
from dotenv import load_dotenv

from .models import TaskResult
from .schemas import GuidelineSummary, Checklist
from .utils import save_task_result

# Load environment variables from .env file
load_dotenv()

# It's best practice to initialize the client once per worker process
# rather than inside the task function.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@shared_task
def hello_world(**kwargs):
    message = kwargs.get("message", "")
    return f"hello world {message}"

@shared_task
def long_running_task(**kwargs):
    """
    A test task that sleeps for a given duration and returns a message.
    """
    duration = kwargs.get("duration", 0)
    message = kwargs.get("message", "")
    time.sleep(duration)
    return f"Slept for {duration} seconds. Message: {message}"

@shared_task(bind=True)
def generate_checklist_from_guidelines(self, **kwargs):
    """
    Celery task to generate a checklist from guidelines using a two-step
    OpenAI API call, with structured output enforced by Pydantic models.
    """
    job_id = self.request.id
    guidelines_text = kwargs.get('guidelines')

    if not guidelines_text:
        raise ValueError("The 'guidelines' key is required in the payload.")

    try:
        # --- Step 1: Summarize Guidelines ---
        summary_prompt = f"""
        Please summarize the following guidelines into a concise paragraph.
        Guidelines: "{guidelines_text}"
        
        Respond with a JSON object matching this schema:
        {{
          "summary": "string"
        }}
        """
        
        summary_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": summary_prompt}],
            response_format={"type": "json_object"}
        )
        
        summary_data = json.loads(summary_response.choices[0].message.content)
        validated_summary = GuidelineSummary(**summary_data)
        summary = validated_summary.summary

        # --- Step 2: Generate Checklist from Summary ---
        checklist_prompt = f"""
        Based on the following summary, generate a detailed checklist of action items.
        Summary: "{summary}"

        Respond with a JSON object matching this schema:
        {{
          "items": [
            {{
              "task": "string",
              "is_complete": false
            }}
          ]
        }}
        """

        checklist_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": checklist_prompt}],
            response_format={"type": "json_object"}
        )

        checklist_data = json.loads(checklist_response.choices[0].message.content)
        validated_checklist = Checklist(**checklist_data)

        # --- Step 3: Persist the final output ---
        final_result = {
            'summary': summary,
            'checklist': validated_checklist.dict()['items']
        }

        save_task_result(
            job_id=job_id,
            task_name=self.name,
            result=final_result
        )
        
        return {'status': 'SUCCESS', 'result': final_result}

    except ValidationError as e:
        self.update_state(state='FAILURE', meta={'error_type': 'PydanticValidationError', 'details': str(e)})
        raise e
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error_type': type(e).__name__, 'details': str(e)})
        raise e

@shared_task(bind=True)
def save_task_result_test_task(self, **kwargs):
    """
    A test task that calls the save_task_result utility function.
    """
    job_id = self.request.id
    task_name = self.name
    
    # Use the payload as the result, or a default if not provided
    result = kwargs if kwargs is not None else {"status": "SUCCESS"}

    save_task_result(job_id, task_name, result)
    
    return result