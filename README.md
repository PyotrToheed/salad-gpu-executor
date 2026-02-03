# Salad Cloud GPU Instance - Docker Image

GPU-accelerated code execution environment for Salad Cloud deployment.

## 📁 Project Structure

```
GPU Instance Project Setup/
├── Dockerfile          # NVIDIA CUDA 12.1 base image configuration
├── requirements.txt    # Python dependencies
├── main.py            # FastAPI server with code execution endpoint
├── s3_test.py         # S3 connectivity verification script
├── .dockerignore      # Files excluded from Docker build
└── README.md          # This file
```

## 🚀 Quick Start

### Build the Docker Image

```bash
docker build -t salad-gpu-executor .
```

### Run Locally (for testing)

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  salad-gpu-executor
```

### Test S3 Connectivity

```bash
docker run --rm \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  salad-gpu-executor python3 s3_test.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON_EXECUTE_TIMEOUT` | `3600` | Max code execution time (seconds) |
| `AWS_ACCESS_KEY_ID` | - | S3 access key |
| `AWS_SECRET_ACCESS_KEY` | - | S3 secret key |
| `AWS_REGION` | `us-east-1` | AWS region |
| `S3_BUCKET_NAME` | `narrated` | Target S3 bucket |
| `SOUNDFONT_PATH` | `/usr/share/sounds/sf2/FluidR3_GM.sf2` | SoundFont file location |

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health with GPU info |
| `/v1/code/execute/python` | POST | Execute Python code |
| `/v1/info` | GET | Instance and package info |

### Execute Code Example

```bash
curl -X POST http://localhost:8000/v1/code/execute/python \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello GPU!\")"}'
```

## 📦 Included Libraries

- **Audio**: pyFluidSynth, mido, pychord, pydub, librosa
- **Video**: PySceneDetect, ffmpeg
- **Geo**: geopandas, contextily
- **Viz**: morethemes, mplcyberpunk, matplotlib
- **Cloud**: boto3 (S3)

## 🎵 SoundFont

FluidR3_GM.sf2 is automatically downloaded during build to `/usr/share/sounds/sf2/`.
