#!/bin/bash
set -e

# Install system dependencies (only if not already installed)
if ! command -v gcc &> /dev/null; then
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*
fi

# Install/upgrade Python dependencies (pip will skip already installed packages)
pip install --quiet --upgrade -r /app/requirements.txt

# Start the API with hot-reload
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

