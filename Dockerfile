# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only (much smaller)
RUN apt-get update && apt-get install -y \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install from wheels (faster, no compilation needed)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/*

# Copy application code
COPY . /app/

# Create non-root user for security
RUN useradd -m -u 1000 django && \
    chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Environment variable
ENV DJANGO_ASGI_MODULE=app.asgi:application

# Run Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "app.asgi:application"]