# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

[![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml)
[![Pytest](https://github.com/swe-students-fall2025/4-containers-charlotte/actions/workflows/tests.yml/badge.svg)](https://github.com/swe-students-fall2025/4-containers-charlotte/actions/workflows/tests.yml)

## Echo - Translation with Voice Cloning

> Translate your voice into English while preserving your unique vocal characteristics using AI-powered speech recognition and voice cloning.

## Team Members

- [Hyunkyu Park](https://github.com/hyunkyuu)
- [Samuel Yang](https://github.com/SamuelYang24)
- [Chengqi Li](https://github.com/lichengqi617)
- [Matthew Zhou](https://github.com/mzhou3299)
- [Nicole Zhang](https://github.com/chzzznn)

---

## Table of Contents

- [About the Project](#about-the-project)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development](#development)

---

## About the Project

**Echo** is a containerized voice translation system. The application takes audio input in any language, translates it to English, and generates the translated speech in the user's original voice using voice cloning technology.

### What It Does

1. **Upload Audio** - Users upload audio files through a web interface
2. **Speech Recognition** - Whisper AI transcribes and detects the source language
3. **Translation** - Automatic translation to English text
4. **Voice Cloning** - TTS (Text-to-Speech) generates English speech in the user's voice
5. **History Tracking** - All translations are stored with user authentication

---

## System Architecture

The application consists of three independent containerized services:

```text
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Web App       │─────▶│  ML Client       │      │  MongoDB    │
│  (Flask)        │      │  (Flask API)     │      │             │
│  Port: 5000     │      │  Port: 5001      │      │ Port: 27017 │
│                 │      │                  │      │             │
│ - User Auth     │      │ - Whisper AI     │      │ - Users     │
│ - Upload UI     │      │ - TTS Cloning    │      │ - History   │
│ - History View  │      │ - Audio Process  │      │ - GridFS    │
└─────────────────┘      └──────────────────┘      └─────────────┘
        │                         │                        │
        └─────────────────────────┴────────────────────────┘
```

---

## Getting Started

### Prerequisites

Before running this application, ensure you have the following installed

- **Docker Desktop** (macOS/Windows) or **Docker Engine + Docker Compose** (Linux)
- **Git** - for cloning the repository
- **Python** - for cloning the repository

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/swe-students-fall2025/4-containers-charlotte.git
cd 4-containers-charlotte
```

#### 2. Set up environment variables

```bash
cp .env.example .env
```

#### 3. Review and customize the `.env` file

```bash
nano .env  # or use your preferred editor
```

---

## Environment Variables

The application uses the following environment variables (defined in `.env`):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | - | Yes |
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017` | Yes |
| `MONGO_DB` | Database name | `db_name` | Yes |
| `TRANSCRIBER_MODEL_SIZE` | Whisper model size (tiny/base/small/medium/large) | `base` | No |
| `DEVICE` | ML processing device (cpu/cuda) | `cpu` | No |
| `CLIENT_URL` | ML client URL for web app | `http://ml:5001` | No |

---

## Running the Application

### Start all containers

```bash
docker-compose up --build
```

This will:

- Build the web app and ML client Docker images
- Download the MongoDB image
- Start all three containers
- Download ML models on first run (may take several minutes)

### Access the application

- **Web Interface**: [http://localhost:5000](http://localhost:5000)
- **ML API**: [http://localhost:5000](http://localhost:5001/api)
- **MongoDB**: localhost:27017

### Stop the application

```bash
docker-compose down
```

To stop and remove all data (including database):

```bash
docker-compose down -v
```

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       ├── lint.yml          # Linting workflow
│       └── tests.yml         # Testing workflow
├── machine-learning-client/
│   ├── app/
│   │   ├── __init__.py       # Flask app factory
│   │   ├── config.py         # Configuration
│   │   ├── db.py             # Database connection
│   │   ├── api/
│   │   │   └── routes.py     # API endpoints
│   │   ├── models/
│   │   │   ├── transcriber.py    # Whisper
│   │   │   └── voice_cloner.py   # TTS
│   │   └── services/
│   │       └── processor.py  # Processing logic
│   ├── tests/                # Unit tests
│   ├── Dockerfile
│   └── Pipfile
├── web-app/
│   ├── templates/           # HTML templates
│   ├── tests/               # Unit tests
│   ├── app.py               # Flask app
│   ├── auth.py              # Authentication
│   ├── models.py            # User model
│   ├── db.py                # Database
│   ├── Dockerfile
│   └── Pipfile
├── docker-compose.yml       # Container orchestration
├── .env.example             # Environment template
└── README.md                # This file
```

---

## Development

### Running Tests

**Machine Learning Client:**

```bash
cd machine-learning-client
pipenv install --dev
pipenv run pytest tests/
```

**Web App:**

```bash
cd web-app
pipenv install --dev
pipenv run pytest tests/
```

### View Logs

View logs for specific containers:

```bash
# All containers
docker-compose logs

# Specific container
docker-compose logs web
docker-compose logs ml
docker-compose logs mongodb

# Follow logs in real-time
docker-compose logs -f
```

---

## Acknowledgments

- **OpenAI Whisper** - Speech recognition model
- **Coqui TTS** - Voice cloning technology
