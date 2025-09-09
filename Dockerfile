# Multi-stage build for production efficiency
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Set labels for better container management
LABEL maintainer="Library Management System Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Library Management System" \
      org.label-schema.description="A comprehensive library management system with advanced features" \
      org.label-schema.url="https://github.com/ambicuity/Library-Management" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/ambicuity/Library-Management" \
      org.label-schema.vendor="Library Management System" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    LIBRARY_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 1000 appuser \
    && useradd -r -u 1000 -g appuser appuser

# Create application directory and set permissions
WORKDIR /app
RUN chown -R appuser:appuser /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/backups /app/translations /app/static /app/templates \
    && chown -R appuser:appuser /app/data /app/logs /app/backups /app/translations /app/static /app/templates

# Switch to non-root user
USER appuser

# Create a startup script
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

# Function to handle graceful shutdown
graceful_shutdown() {
    echo "Received SIGTERM signal, shutting down gracefully..."
    if [ ! -z "$API_PID" ]; then
        kill -TERM "$API_PID" 2>/dev/null || true
    fi
    if [ ! -z "$WEB_PID" ]; then
        kill -TERM "$WEB_PID" 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap graceful_shutdown SIGTERM SIGINT

# Initialize the application
echo "Initializing Library Management System..."

# Create default admin user if none exists
python -c "
from library_management_system.auth import AuthManager, Role
auth = AuthManager()
if not auth.users:
    auth.create_user('admin', 'admin@library.local', 'admin123', Role.ADMIN)
    print('Default admin user created: admin/admin123')
else:
    print('Users already exist, skipping default user creation')
"

# Start services based on environment variables
if [ "$START_MODE" = "api" ]; then
    echo "Starting API server..."
    python -c "
from library_management_system.api import create_api
api = create_api()
api.run(host='0.0.0.0', port=8000)
    " &
    API_PID=$!
    echo "API server started with PID $API_PID"
    
elif [ "$START_MODE" = "web" ]; then
    echo "Starting web interface..."
    python -c "
from library_management_system.web_interface import create_web_interface
web = create_web_interface()
web.run(host='0.0.0.0', port=8000)
    " &
    WEB_PID=$!
    echo "Web interface started with PID $WEB_PID"
    
elif [ "$START_MODE" = "cli" ]; then
    echo "Starting CLI interface..."
    python library_management.py
    
else
    echo "Starting both API and web interface..."
    
    # Start API server
    python -c "
from library_management_system.api import create_api
api = create_api()
api.run(host='0.0.0.0', port=8000)
    " &
    API_PID=$!
    echo "API server started on port 8000 with PID $API_PID"
    
    # Start web interface
    python -c "
from library_management_system.web_interface import create_web_interface
web = create_web_interface()
web.run(host='0.0.0.0', port=8080)
    " &
    WEB_PID=$!
    echo "Web interface started on port 8080 with PID $WEB_PID"
fi

# Wait for processes to complete
if [ ! -z "$API_PID" ]; then
    wait $API_PID
fi
if [ ! -z "$WEB_PID" ]; then
    wait $WEB_PID
fi

echo "Library Management System stopped"
EOF

# Make startup script executable
RUN chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8080

# Define volumes for persistent data
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Set default command
CMD ["/app/start.sh"]

# Development stage
FROM production as development

# Switch back to root to install development dependencies
USER root

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Switch back to appuser
USER appuser

# Override startup for development
CMD ["python", "library_management.py"]