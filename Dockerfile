# Miss_TaskMaster Main Application Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create required directories
RUN mkdir -p /app/work_logs /app/mcp_server /app/project_state

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY project_plan_template.json .

# Copy MCP server files
COPY mcp_server/ ./mcp_server/

# Make sure scripts are executable
RUN chmod +x main.py
RUN chmod +x mcp_server/main.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --user-group --system --uid 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports for different services
EXPOSE 8000
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command runs the MCP server
CMD ["python", "mcp_server/main.py"]