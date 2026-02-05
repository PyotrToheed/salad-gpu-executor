FROM nvidia/cuda:12.1.0-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHON_EXECUTE_TIMEOUT=3600

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    ffmpeg \
    fluidsynth \
    libfluidsynth-dev \
    fluid-soundfont-gm \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# SoundFont is installed via APT package (fluid-soundfont-gm)
# Path: /usr/share/sounds/sf2/FluidR3_GM.sf2

ENV SOUNDFONT_PATH=/usr/share/sounds/sf2/FluidR3_GM.sf2

COPY main.py .
COPY s3_test.py .

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
