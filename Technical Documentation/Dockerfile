FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all project files
COPY . /code/

# Make wait script executable
RUN chmod +x /code/wait-for-postgres.sh

# Collect static files (optional, avoid error if static setup is missing)
RUN python manage.py collectstatic --noinput || true

CMD ["./wait-for-postgres.sh"]
