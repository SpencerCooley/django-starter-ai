import pytest
import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestJobViewIntegration:
    """
    Integration tests for the JobView API endpoint that test the full
    request-to-celery-to-result workflow.
    """

    def setup_method(self):
        """
        Set up the test client for each test method.
        """
        self.client = APIClient()
        self.job_url = reverse('job')

    def test_long_running_task_workflow(self):
        """
        Test the full workflow of creating a task, polling for its status,
        and verifying its successful completion.
        """
        # 1. Define the job and its parameters
        task_duration = 5
        task_message = "Integration Test"
        job_data = {
            "job_name": "api.tasks.long_running_task",
            "payload": {
                "duration": task_duration,
                "message": task_message
            }
        }

        # 2. Make the POST request to create the job
        response = self.client.post(self.job_url, job_data, format='json')
        assert response.status_code == status.HTTP_202_ACCEPTED
        task_id = response.data.get('task_id')
        assert task_id is not None

        # 3. Poll the status endpoint until the task is complete
        start_time = time.time()
        timeout = task_duration + 10  # Add a 10-second buffer
        final_status = None

        while time.time() - start_time < timeout:
            status_url = f"{self.job_url}?job_id={task_id}"
            status_response = self.client.get(status_url)
            assert status_response.status_code == status.HTTP_200_OK
            
            current_status = status_response.data.get('status')
            if current_status in ['SUCCESS', 'FAILURE']:
                final_status = current_status
                break
            
            # Optional: Check for intermediate states
            assert current_status in ['PENDING', 'STARTED']
            time.sleep(1)

        # 4. Assert the final state
        assert final_status == 'SUCCESS', f"Task did not complete successfully. Final status was {final_status}"
        
        # Re-fetch the final result to be sure
        final_response = self.client.get(f"{self.job_url}?job_id={task_id}")
        expected_result = f"Slept for {task_duration} seconds. Message: {task_message}"
        assert final_response.data.get('result') == expected_result