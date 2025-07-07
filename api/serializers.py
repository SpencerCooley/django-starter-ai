
from rest_framework import serializers

class JobCreateRequestSerializer(serializers.Serializer):
    """
    Serializer for creating a new job. Defines the expected request body.
    """
    job_name = serializers.CharField(
        help_text="The full import path to the Celery task (e.g., 'api.tasks.hello_world')."
    )
    payload = serializers.JSONField(
        required=False,
        help_text="A JSON object containing the payload to be passed to the Celery task."
    )

class JobCreateResponseSerializer(serializers.Serializer):
    """
    Serializer for the response when a job is successfully created.
    """
    task_id = serializers.CharField(help_text="The unique ID of the created Celery task.")

class JobStatusResponseSerializer(serializers.Serializer):
    """
    Serializer for the response when checking a job's status.
    """
    task_id = serializers.CharField(help_text="The ID of the Celery task.")
    status = serializers.CharField(help_text="The current status of the task (e.g., 'PENDING', 'SUCCESS', 'FAILURE').")
    result = serializers.JSONField(
        allow_null=True,
        help_text="The result of the task if it has completed successfully. Can be any JSON value."
    )
