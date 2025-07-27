from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from celery_config import echo_with_delay, celery_app # Import celery_app itself
from queue_manager import add_to_queue, get_position

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {
        "service": "Task Queue API",        
        "description": "Distributed task processing system with Celery, RabbitMQ, and Redis",
        "version": "1.0.0",
        "POST": "/api/v1/tasks",
        "GET": "/api/v1/tasks/{task_id}"
    }

@app.post("/api/v1/tasks")
def run_echo_task(text: str = Body(..., embed=True)):
    print(f"FastAPI: Received request for text: {text}")
    task = echo_with_delay.delay(text)
    add_to_queue(task.id)
    print(f"FastAPI: Task {task.id} dispatched and added to custom queue.")
    return {
        "message": "Task dispatched successfully",
        "task_id": task.id
    }

@app.get("/api/v1/tasks/{task_id}")
def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    
    queue_position = None
    if not task.ready():
        queue_position = get_position(task_id)
    
    if task.ready(): 
        
        result = task.result if task.successful() else str(task.result)
        print(f"FastAPI: Task {task_id} is READY. Status: {task.status}. Result: {result[:50]}...")
        return {
            "task_id": task.id,
            "status": task.status,
            "result": result,
            "queue_position": None 
        }
    
    print(f"FastAPI: Task {task_id} is NOT READY. Status: {task.status}. Queue Position: {queue_position}")
    return {
        "task_id": task.id,
        "status": task.status, 
        "result": None,
        "queue_position": queue_position 
    }
