
from .models import TaskResult

def save_task_result(job_id: str, task_name: str, result: dict):
    """
    A helper function to create a TaskResult entry in the database.
    
    Args:
        job_id: The Celery task's unique ID.
        task_name: The name of the task that was run.
        result: A JSON-serializable dictionary containing the task's output.
    """
    TaskResult.objects.create(
        job_id=job_id,
        task_name=task_name,
        result=result
    )
