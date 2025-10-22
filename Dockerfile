# Fix 1: Use a currently supported Debian version (Bullseye or Bookworm)
# 'python:3.11-slim' is preferred as it automatically tracks stable distributions.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if needed, e.g., for psycopg2)
# RUN apt-get update && apt-get install -y \
#    libpq-dev \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the container
COPY . /app/

# Expose the port Daphne will listen on
EXPOSE 8000

# *** IMPORTANT: Replace 'app.asgi:application' with your actual Django ASGI path ***
ENV DJANGO_ASGI_MODULE=app.asgi:application

# Run Daphne, binding to all interfaces and using the defined module
# The -b (bind) and -p (port) flags ensure it listens correctly inside the container.
# Using the shell form of CMD ensures the environment variable is expanded.
CMD daphne -b 0.0.0.0 -p 8000 $DJANGO_ASGI_MODULE