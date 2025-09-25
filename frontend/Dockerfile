# Multi-stage build for Frontend
FROM python:3.13-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Production stage
FROM python:3.13-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Add venv to path
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Create vector_store directory with proper permissions (shared with mcp-server)
RUN mkdir -p /vector_store && chown appuser:appuser /vector_store

# Create chainlit directories
RUN mkdir -p /app/.chainlit && chown -R appuser:appuser /app/.chainlit

# Switch to non-root user
USER appuser

# Health check endpoint (chainlit health check)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Set chainlit configuration
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=8001

# Run the Chainlit application
CMD ["uv", "run", "python", "-m", "chainlit", "run", "chainlit_app.py", "--port", "8001", "--host", "0.0.0.0"]