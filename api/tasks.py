
from celery import shared_task

@shared_task
def hello_world(payload):
    message = payload.get("message", "")
    return f"hello world {message}"
