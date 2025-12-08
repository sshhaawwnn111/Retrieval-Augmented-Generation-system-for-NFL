<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
=======
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip

# 1. Install Torch specifically from the index (using --index-url, NOT extra)
# This forces pip to ONLY look here for these packages
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY requirements.txt ./

# 2. Install the rest (remove torch from requirements.txt or keep it, pip will see it's already satisfied)
RUN pip3 install --no-cache-dir -r requirements.txt
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86

COPY . /app

ENV PYTHONUNBUFFERED=1
<<<<<<< HEAD

CMD ["python", "main.py"]
=======
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

EXPOSE 8002


HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86
