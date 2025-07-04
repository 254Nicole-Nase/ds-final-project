FROM python:3.10-slim

RUN apt-get update && apt-get install -y docker.io curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY balancer.py .
COPY hashing.py .

EXPOSE 5000
CMD ["python", "balancer.py"]

