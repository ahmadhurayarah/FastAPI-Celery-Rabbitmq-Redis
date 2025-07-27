import os
import time
from celery import Celery
from dotenv import load_dotenv
from celery.signals import task_prerun, task_postrun, task_success, task_failure

# Load environment variables from .env file
load_dotenv()

# Configure Celery with RabbitMQ as broker and Redis as backend
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")

REDIS_URL = os.getenv("REDIS_URL")

broker_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
backend_url = REDIS_URL

celery_app = Celery(
    'celery_app',
    broker=broker_url,
    backend=backend_url
)

# IMPORTANT: Import queue_manager AFTER celery_app is defined
from queue_manager import remove_from_queue

@celery_app.task(bind=True) # Make the task a bound task
def echo_with_delay(self, text): # 'self' is now the first argument
    # CORRECT WAY to get the current task ID in a bound task
    task_id = self.request.id 
    
    print(f"Celery Task: Processing task {task_id} with text: {text}")
    
    time.sleep(20) # Task takes 20 seconds
    print(f"Celery Task: Task {task_id} finished.")
    print(f"***************************************8")
    return text

# Signal handler: This function will be called right before a task starts executing
@task_prerun.connect
def handle_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **_kwargs):
    """
    Removes the task from the custom Redis queue when the Celery worker starts processing it.
    """
    print(f"Celery Signal (prerun): Task {task_id} is starting. Attempting to remove from custom queue.")
    remove_from_queue(task_id)

# Fallback signal (optional, but good for robustness)
@task_postrun.connect
def handle_task_postrun(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **_kwargs):
    """
    This signal fires after a task has run, regardless of success or failure.
    Ensures removal if prerun somehow failed or if task was revoked/failed.
    """
    if state in ['SUCCESS', 'FAILURE', 'REVOKED']:
        print(f"Celery Signal (postrun): Task {task_id} finished with state {state}. Ensuring removal from custom queue.")
        remove_from_queue(task_id)

@task_success.connect
def handle_task_success(sender=None, result=None, **_kwargs):
    print(f"Celery Signal (success): Task {sender.request.id} succeeded.")

@task_failure.connect
def handle_task_failure(sender=None, exc=None, traceback=None, einfo=None, **_kwargs):
    print(f"Celery Signal (failure): Task {sender.request.id} failed with exception: {exc}")
