# syntax=docker/dockerfile:1.7

############################
# Builder: make dependency wheels
############################
FROM python:3.12-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1

# Build tools (removed from final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc git pkg-config curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only dependency manifests first for better cache hits
COPY requirements.txt ./
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip wheel --wheel-dir /wheels -r requirements.txt

# Bring in app code and precompile bytecode (optional)
WORKDIR /src
COPY . .
RUN python -m compileall -q .

############################
# Runtime: tiny image
############################
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONOPTIMIZE=2

# Non-root
RUN useradd -r -u 10001 app
WORKDIR /app

# Install deps from wheels (no compilers needed)
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
 && pip install --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

# Copy app
COPY --from=builder /src /app
RUN chown -R app:app /app
USER app

# If your app serves HTTP, set PORT env outside
# EXPOSE 8000
ENTRYPOINT ["python", "-OO", "main.py"]
