FROM python:3.10

# System deps + build tools
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    sudo ffmpeg git pkg-config \
    libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev \
    libswscale-dev libswresample-dev libavfilter-dev aria2 unzip \
    build-essential gcc g++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install OpenVoice
WORKDIR /app
RUN git clone https://github.com/myshell-ai/OpenVoice openvoice
WORKDIR /app/openvoice

# Install build dependencies first
RUN pip install --no-cache-dir "cython<3.0.0" numpy

# Install OpenVoice without problematic dependencies
RUN pip install --no-cache-dir -e . --no-deps
RUN pip install --no-cache-dir librosa==0.9.1 pydub wavmark torch torchaudio

# Download OpenVoice checkpoints
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    https://huggingface.co/camenduru/OpenVoice/resolve/main/checkpoints_1226.zip \
    -d /app/openvoice -o checkpoints_1226.zip \
 && unzip /app/openvoice/checkpoints_1226.zip \
 && mv checkpoints openvoice/checkpoints \
 && mv resources openvoice/resources \
 && rm checkpoints_1226.zip

# Install Whisper and other dependencies
RUN pip install --no-cache-dir openai-whisper python-dotenv pymongo

# Copy our application code
WORKDIR /app/ml-client
COPY *.py ./
COPY requirements.txt ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENVOICE_CONVERTER_CKPT=/app/openvoice/openvoice/checkpoints

# Run our ML client
CMD ["python", "main.py"]
