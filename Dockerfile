# Use Python 3.11 slim image (Debian-based)
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
# Use --no-binary for problematic packages to avoid pre-built wheels issues
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

# Expose port 8000
EXPOSE 8000

# Set environment variable for Django ASGI module
ENV DJANGO_ASGI_MODULE=app.asgi:application

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000')" || exit 1

# Run Daphne server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]