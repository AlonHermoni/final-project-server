# Use Python 3.9 runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port (Cloud Run will set PORT environment variable)
EXPOSE 8080

# Use gunicorn with eventlet worker for WebSocket support
# Note: For SocketIO with eventlet, we target the Flask app object
CMD exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 "app:app"