# Multi-stage Dockerfile for Daily Tracker
# Stage 1: Builder - Install dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies to a virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install --no-cache-dir .

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 tracker && \
    mkdir -p /home/tracker/.config/tracker && \
    chown -R tracker:tracker /home/tracker

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=tracker:tracker . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL="sqlite:////home/tracker/.config/tracker/tracker.db"

# Switch to non-root user
USER tracker

# Create database directory
RUN mkdir -p /home/tracker/.config/tracker

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health').read()"

# Expose port
EXPOSE 8000

# Default command: run API server
CMD ["uvicorn", "tracker.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]
