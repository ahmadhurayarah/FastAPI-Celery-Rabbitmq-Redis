# Celery-RabbitMQ Distributed Task Queue

A robust distributed task processing system built with FastAPI, Celery, RabbitMQ, and Redis. This project provides a scalable solution for handling long-running tasks with real-time status tracking and queue position monitoring.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │───▶│   Celery    │───▶│  RabbitMQ   │───▶│   Workers   │
│   (API)     │    │ (Task Queue)│    │ (Message    │    │ (Processing)│
│             │    │             │    │  Broker)    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │   Redis     │    │   Redis     │    │   Redis     │
│ (Frontend)  │    │ (Results)   │    │ (Custom     │    │ (Queue      │
│             │    │             │    │  Queue)     │    │ Position)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 Features

- **Asynchronous Task Processing**: Handle long-running tasks without blocking
- **Real-time Queue Position Tracking**: Monitor task position in the queue
- **Distributed Architecture**: Scale across multiple workers
- **RESTful API**: Easy integration with any frontend
- **Robust Error Handling**: Comprehensive error management and logging
- **Message Persistence**: No task loss with RabbitMQ
- **CORS Support**: Ready for web frontend integration

## 📋 Prerequisites

- Python 3.8+
- RabbitMQ Server
- Redis Server
- Docker (optional, for containerized setup)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ahmadhurayarah/FastAPI-Celery-Rabbitmq-Redis.git
cd FastAPI-Celery-Rabbitmq-Redis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 4. Start Services

#### Option A: Using Docker Compose (Recommended)

```bash
# Start RabbitMQ and Redis
docker-compose up -d
```

#### Option B: Manual Setup

```bash
# Start RabbitMQ (if installed locally)
sudo systemctl start rabbitmq-server

# Start Redis (if installed locally)
sudo systemctl start redis-server
```

## 🚀 Running the Application

### 1. Start the FastAPI Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Celery Worker

```bash
celery -A celery_config worker --loglevel=info
```

### 3. Start Celery Beat (Optional - for scheduled tasks)

```bash
celery -A celery_config beat --loglevel=info
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. Service Information

```http
GET /
```

**Response:**

```json
{
  "service": "Task Queue API",
  "description": "Distributed task processing system with Celery, RabbitMQ, and Redis",
  "version": "1.0.0",
  "POST": "/api/v1/tasks",
  "GET": "/api/v1/tasks/{task_id}"
}
```

#### 2. Submit Task

```http
POST /api/v1/tasks
Content-Type: application/json

{
  "text": "Hello, World!"
}
```

**Response:**

```json
{
  "message": "Task dispatched successfully",
  "task_id": "12345678-1234-1234-1234-123456789abc"
}
```

#### 3. Check Task Status

```http
GET /api/v1/tasks/{task_id}
```

**Response (Task Pending):**

```json
{
  "task_id": "12345678-1234-1234-1234-123456789abc",
  "status": "PENDING",
  "result": null,
  "queue_position": 3
}
```

**Response (Task Completed):**

```json
{
  "task_id": "12345678-1234-1234-1234-123456789abc",
  "status": "SUCCESS",
  "result": "Hello, World!",
  "queue_position": null
}
```

## 🔧 Configuration

### Environment Variables

| Variable        | Description          | Default                    |
| --------------- | -------------------- | -------------------------- |
| `RABBITMQ_HOST` | RabbitMQ server host | `localhost`                |
| `RABBITMQ_PORT` | RabbitMQ server port | `5672`                     |
| `RABBITMQ_USER` | RabbitMQ username    | `guest`                    |
| `RABBITMQ_PASS` | RabbitMQ password    | `guest`                    |
| `REDIS_URL`     | Redis connection URL | `redis://localhost:6379/0` |

### Task Configuration

- **Processing Time**: 20 seconds (configurable in `celery_config.py`)
- **Queue Name**: `celery_task_queue` (configurable in `queue_manager.py`)
- **Task Type**: Echo task (returns input text after processing)

## 📁 Project Structure

```
celery-rabbitmq/
├── app.py              # FastAPI application
├── celery_config.py    # Celery configuration and tasks
├── queue_manager.py    # Custom queue management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## 🔍 Monitoring and Debugging

### Celery Monitoring

```bash
# Monitor Celery workers
celery -A celery_config inspect active

# Check task statistics
celery -A celery_config inspect stats
```

### Redis Queue Monitoring

```bash
# Connect to Redis CLI
redis-cli

# Check queue length
LLEN celery_task_queue

# View queue contents
LRANGE celery_task_queue 0 -1
```

### Logs

The application provides comprehensive logging:

- FastAPI request/response logs
- Celery task execution logs
- Queue management logs
- Error and exception logs

## 🧪 Testing

### Using curl

```bash
# Submit a task
curl -X POST "http://localhost:8000/api/v1/tasks" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test message"}'

# Check task status (replace with actual task_id)
curl "http://localhost:8000/api/v1/tasks/your-task-id-here"
```

### Using Python

```python
import requests
import time

# Submit task
response = requests.post(
    "http://localhost:8000/api/v1/tasks",
    json={"text": "Hello from Python!"}
)
task_id = response.json()["task_id"]

# Monitor task status
while True:
    status_response = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}")
    status_data = status_response.json()

    print(f"Status: {status_data['status']}")
    if status_data['queue_position']:
        print(f"Queue Position: {status_data['queue_position']}")

    if status_data['status'] in ['SUCCESS', 'FAILURE']:
        print(f"Result: {status_data['result']}")
        break

    time.sleep(2)
```

## 🚀 Scaling

### Multiple Workers

```bash
# Start multiple workers on different machines
celery -A celery_config worker --loglevel=info --hostname=worker1@%h
celery -A celery_config worker --loglevel=info --hostname=worker2@%h
```

### Load Balancing

The system automatically distributes tasks across available workers using RabbitMQ's round-robin distribution.

## 🔒 Security Considerations

- Use strong passwords for RabbitMQ and Redis in production
- Implement authentication for the FastAPI endpoints
- Use HTTPS in production environments
- Consider using Redis SSL/TLS for secure connections
- Implement rate limiting for API endpoints

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused Errors**

   - Ensure RabbitMQ and Redis are running
   - Check environment variables in `.env` file
   - Verify network connectivity

2. **Tasks Not Processing**

   - Check if Celery workers are running
   - Verify RabbitMQ connection
   - Check worker logs for errors

3. **Queue Position Not Updating**
   - Ensure Redis is accessible
   - Check queue manager logs
   - Verify task signal handlers are working

### Debug Commands

```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Celery worker status
celery -A celery_config inspect ping
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details
