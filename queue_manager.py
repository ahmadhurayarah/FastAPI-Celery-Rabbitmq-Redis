import os
import redis
from dotenv import load_dotenv

# Ensure .env is loaded here for standalone use or when imported by celery_config
load_dotenv() 

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable not set. Please set it in your .env file.")

# Initialize Redis client
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("Queue Manager: Successfully connected to Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"Queue Manager: Could not connect to Redis: {e}")
    print("Queue Manager: Please ensure your REDIS_URL in .env is correct and Redis server is running.")
    # Do not exit here, as this module might be imported by FastAPI which should still run.
    # However, queue operations will fail.

QUEUE_NAME = "celery_task_queue"

def add_to_queue(task_id: str):
    """Adds a task ID to the right (end) of the Redis list representing the queue."""
    try:
        redis_client.rpush(QUEUE_NAME, task_id)
        print(f"Queue Manager: Added task {task_id} to queue. Current queue length: {redis_client.llen(QUEUE_NAME)}")
    except redis.RedisError as e:
        print(f"Queue Manager: Redis error adding task {task_id} to queue: {e}")

def remove_from_queue(task_id: str):
    """Removes all occurrences of a task ID from the Redis list."""
    try:
        initial_length = redis_client.llen(QUEUE_NAME)
        print(f"Queue Manager: Before removal, queue '{QUEUE_NAME}' has {initial_length} items. Checking for task: {task_id}")
        
        # Check if the task_id is actually in the queue before attempting to remove
        queue_contents = redis_client.lrange(QUEUE_NAME, 0, -1)
        if task_id not in queue_contents:
            print(f"Queue Manager: Task {task_id} NOT found in queue before lrem. No removal needed.")
            return # Exit if not found

        # lrem(key, count, value): count=0 removes all occurrences
        removed_count = redis_client.lrem(QUEUE_NAME, 0, task_id)
        final_length = redis_client.llen(QUEUE_NAME)
        
        print(f"Queue Manager: Attempted to remove task {task_id}. lrem returned {removed_count} instances removed. Queue length changed from {initial_length} to {final_length}.")
        
        if removed_count == 0 and task_id in queue_contents:
            print(f"Queue Manager: WARNING! Task {task_id} was found in queue but lrem reported 0 removals. This indicates a problem.")
            
    except redis.RedisError as e:
        print(f"Queue Manager: Redis error removing task {task_id} from queue: {e}")

def get_position(task_id: str):
    """
    Gets the 1-based position of a task ID in the Redis list.
    Returns None if the task ID is not found or on Redis error.
    """
    try:
        queue = redis_client.lrange(QUEUE_NAME, 0, -1)
        if task_id in queue:
            position = queue.index(task_id) + 1
            print(f"Queue Manager: Task {task_id} found at position {position}.")
            return position
        print(f"Queue Manager: Task {task_id} not found in queue.")
        return None # Task not found in the queue
    except redis.RedisError as e:
        print(f"Queue Manager: Redis error getting position for {task_id}: {e}")
        return None
    except ValueError: # This should ideally not happen if task_id in queue check passes
        print(f"Queue Manager: ValueError - Task {task_id} not found in list during index lookup.")
        return None
