# Use official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY server.txt .

# Install dependencies
RUN pip install --no-cache-dir -r server.txt

# Copy the FastAPI application
COPY server.py .

# Expose port 5000
EXPOSE 5000

# Command to run the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]