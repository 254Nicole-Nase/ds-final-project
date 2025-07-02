FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
ENV SERVER_ID=""
EXPOSE 5000
CMD ["python", "server.py"]
