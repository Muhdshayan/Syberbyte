# Use a stable Debian-based Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/py/bin:$PATH"

# Install system dependencies using APT
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip

# Set working directory
WORKDIR /backend

# Copy and install dependencies
COPY ./requirements.txt .
RUN /py/bin/pip install -r requirements.txt

# Copy the project code
COPY . .

# Set the default command
CMD ["/py/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
