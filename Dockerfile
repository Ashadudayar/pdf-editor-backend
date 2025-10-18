FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations during build
RUN python manage.py migrate --noinput || echo "Migrations will run at startup"

# Collect static files
RUN python manage.py collectstatic --noinput || echo "No static files"

# Expose port (Railway will override this)
EXPOSE 8000

# CRITICAL: Use $PORT from Railway environment
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info --access-logfile - --error-logfile -