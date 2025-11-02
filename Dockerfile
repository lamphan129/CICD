FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY dashboard/ ./dashboard/
COPY scripts/ ./scripts/


WORKDIR /app/dashboard


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]