FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    docker.io \
    docker-compose \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY autoscaler.py .

CMD ["python", "autoscaler.py"]