FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend, schemas, rulesets, and compiled frontend
COPY schemas /app/schemas
COPY rulesets /app/rulesets
COPY docs /app/docs
COPY backend /app/backend
COPY frontend/dist /app/frontend/dist

EXPOSE 8000
ENV PYTHONPATH=/app/backend

CMD ["python", "backend/main.py"]
