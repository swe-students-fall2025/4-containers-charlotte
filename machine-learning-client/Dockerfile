FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for sudachipy)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install --upgrade pip setuptools wheel pipenv

COPY Pipfile Pipfile.lock ./

# Pre-install PyTorch (CPU version) to avoid compiling from source inside TTS
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install rest of Python dependencies
RUN pipenv install --system --deploy

COPY . .

ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
