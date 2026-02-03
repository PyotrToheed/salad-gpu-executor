# Salad Cloud GPU Docker Image
# Base: NVIDIA CUDA 12.1 with Ubuntu 22.04
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHON_EXECUTE_TIMEOUT=3600

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    ffmpeg \
    fluidsynth \
    libfluidsynth-dev \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Download SoundFont file (FluidR3_GM.sf2)
RUN mkdir -p /usr/share/sounds/sf2 && \
    wget -q -O /usr/share/sounds/sf2/FluidR3_GM.sf2 \
    "https://keymusician01.s3.amazonaws.com/FluidR3_GM.sf2" || \
    wget -q -O /usr/share/sounds/sf2/FluidR3_GM.sf2 \
    "https://github.com/urish/cinto/raw/master/media/FluidR3_GM.sf2"

# Set SoundFont environment variable
ENV SOUNDFONT_PATH=/usr/share/sounds/sf2/FluidR3_GM.sf2

# Copy application files
COPY main.py .
COPY s3_test.py .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
