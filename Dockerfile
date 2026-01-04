# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system dependencies required for Playwright
# We install playwright first to let it handle browser dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN  pip install --no-deps -r requirements.txt
RUN pip install --only-binary=:all: fastapi uvicorn requests beautifulsoup4 playwright

# Install Playwright Browsers (Firefox only to save space/time)
RUN playwright install firefox

# Copy the rest of the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



