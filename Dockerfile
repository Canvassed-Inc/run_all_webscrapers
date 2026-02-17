# Dockerfile
FROM python:3.11-slim

# Prevents Python from writing .pyc files & buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the job launcher
CMD ["python", "main.py"]