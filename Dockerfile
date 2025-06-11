# Use Python 3.11 as the base image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY frontend/requirements.txt frontend-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r frontend-requirements.txt
RUN pip install --no-cache-dir plotly

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Install backend package in development mode
RUN pip install -e /app/backend

# Create startup script
RUN echo '#!/bin/bash\n\
if [ -z "$OPENAI_API_KEY" ]; then\n\
    echo "Error: OPENAI_API_KEY environment variable is not set"\n\
    echo "Please run the container with: docker run -e OPENAI_API_KEY=your_api_key ..."\n\
    exit 1\n\
fi\n\
cd /app\n\
PYTHONPATH=/app/backend uvicorn backend.main:app --host 0.0.0.0 --port 8001 & \n\
streamlit run frontend/streamlit_app.py --server.port 3001 --server.address 0.0.0.0 & \n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8001 3001

# Start both services
CMD ["/app/start.sh"]
