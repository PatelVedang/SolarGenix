FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install CPU only torch first (smaller size)
RUN pip install torch==2.10.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose Hugging Face default port
EXPOSE 7860

# Start server
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "solar_project.wsgi:application"]