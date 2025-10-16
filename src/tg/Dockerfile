# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN adduser --disabled-password --gecos "" bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
USER bot

# Healthcheck: process must be alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import socket,sys; sys.exit(0)"
CMD ["python", "app.py"]

