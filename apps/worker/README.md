# CRDC PreCheck Worker

Celery worker handling asynchronous workloads such as rule execution, evidence packet generation, and connector jobs.

## Running Locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
celery -A worker.app worker --loglevel=info
```

Broker and result backend defaults align with the Docker Compose file (`redis://redis:6379/0`). Override via environment variables when needed.
