from celery import shared_task
import time

@shared_task
def hello_world(payload):
    message = payload.get("message", "")
    return f"hello world {message}"

@shared_task
def long_running_task(duration, message):
    """
    A test task that sleeps for a given duration and returns a message.
    """
    time.sleep(duration)
    return f"Slept for {duration} seconds. Message: {message}"