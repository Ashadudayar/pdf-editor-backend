FROM python:3.11-slim

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    mupdf \
    mupdf-tools \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear || true

# Expose port
EXPOSE 8000

# Start command
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT