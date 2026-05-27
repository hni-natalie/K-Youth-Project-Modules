# Base image
FROM python:3.14-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first (better Docker caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY src ./src

# Expose FastAPI port
EXPOSE 3000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "3000"]