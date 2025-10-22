# Poros Protocol - Backend Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy startup script and application code
COPY start.py /app/start.py
COPY app /app/app

# Expose port
EXPOSE 8000

# Run via Python wrapper that reads PORT env variable
CMD ["python", "start.py"]
