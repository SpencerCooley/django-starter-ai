from django.db import models
import uuid

class TaskResult(models.Model):
    """
    A flexible model to store the output of any Celery task.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The job_id from Celery, to link the task to its result
    job_id = models.CharField(max_length=255, unique=True, db_index=True)
    
    # The name of the task that was run
    task_name = models.CharField(max_length=255, db_index=True)
    
    # The output of the task, stored in a flexible JSON field
    result = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.task_name} ({self.job_id})"