"""
Gunicorn configuration for MecGuraServe
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "8000")
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "warning"

# Process naming
proc_name = "mecguraserve"

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
