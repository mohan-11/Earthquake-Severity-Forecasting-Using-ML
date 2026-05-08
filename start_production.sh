#!/bin/bash

# Production startup script for Earthquake Prediction API

set -e

echo "🚀 Starting Earthquake Prediction API in Production Mode..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  Warning: .env file not found, using default values"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Check if ML model files exist
if [ ! -f "earthquake_model.pkl" ]; then
    echo "❌ Error: earthquake_model.pkl not found. Please train the model first."
    exit 1
fi

if [ ! -f "label_encoder.pkl" ]; then
    echo "❌ Error: label_encoder.pkl not found. Please train the model first."
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the application with Gunicorn
echo "🌐 Starting FastAPI application with Gunicorn..."
exec gunicorn app.main:app \
    --bind ${HOST:-0.0.0.0}:${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --capture-output
