FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY entrypoint.sh /app/entrypoint.sh
COPY . /app/

RUN chmod +x /app/entrypoint.sh

# Collect static files at build time
RUN python manage.py collectstatic --noinput

EXPOSE 8080

WORKDIR /app

ENTRYPOINT ["./entrypoint.sh"]
