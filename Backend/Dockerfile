FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --require-hashes --no-cache-dir -r requirements.txt

COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --no-create-home appuser && chown -R appuser /app
USER appuser

CMD ["gunicorn", "PayFlow_Store.wsgi:application", "--bind", "0.0.0.0:8000"]
