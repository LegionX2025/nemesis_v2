FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_docker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . /app

# Expose the API port
EXPOSE 8000

# Set environment variables for production (can be overridden by the runtime)
ENV HOST=0.0.0.0
ENV PORT=8000

# Start the FastAPI application via uvicorn directly
CMD ["uvicorn", "nemesis_core:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
