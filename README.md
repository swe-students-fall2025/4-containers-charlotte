[![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml)
# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.


## Project Overview

This project is a **voice-cloning translator** built as a containerized system. It:

1. **Listens to your voice** (uploaded audio).
2. Uses **Whisper** to perform:
   - **Speech recognition** (transcription).
   - **Speech translation** into English (or other target languages).
3. Uses **OpenVoice** to:
   - **Clone your voice** from a reference clip.
   - **Generate translated speech** in your cloned voice.
4. Stores user accounts & translation history in **MongoDB**, and exposes all of this via a **Flask web app** dashboard.

Everything runs in three Docker containers, orchestrated with `docker-compose`:

- `machine-learning-client` (Whisper + OpenVoice API)
- `web-app` (Flask UI + auth + history)
- `mongodb` (database)

---
## Prerequisites

Before running the system, ensure the following tools and resources are installed on your machine:

### Required Software
- **Git** — for version control and cloning the repository.
- **Docker & Docker Compose**
  - Docker Desktop (macOS/Windows), or
  - Docker Engine + Docker Compose plugin (Linux)
- **Python 3.10+** (optional, only needed for local development outside of Docker)
- **pip** or **pipenv** — for managing Python packages during local testing.

### Hardware & Storage Requirements
- Enough disk space to store:
  - Whisper model weights (from 150 MB to 3 GB depending on model size)
  - OpenVoice checkpoints (typically 500 MB – 1.5 GB)
  - Processed audio outputs (user-generated)

### Machine Learning Model Dependencies

The machine learning client requires several ML libraries (installed automatically inside the Docker container):


During Docker image build, these packages are installed based on  
**machine-learning-client/requirements.txt**.

### Model Installation Notes

The ML container must have access to the pretrained model files:

1. **Whisper model**
   - Automatically downloaded at runtime on first use, *OR*
   - Pre-downloaded and mounted into the container for faster inference.

2. **OpenVoice model**
   - Checkpoint and config files must be:
     - downloaded during image build, *or*
     - stored in a `/models` directory and mounted as a volume:
       ```yaml
       volumes:
         - ml-models:/models
       ```

Your actual model locations are configured through environment variables (see next section).


---

## System Architecture

**Subsystems**

1. **Machine Learning Client (ML API) – container 1**
   - Flask service exposing ML endpoints:
     - `/transcribe` – Whisper transcription.
     - `/translate` – Whisper translation to English.
     - `/voice-clone` – OpenVoice voice cloning + TTS.
     - `/download/<filename>` – download generated audio.
     - `/process` – end-to-end pipeline (translate + clone).
   - Handles:
     - File upload & validation (`ALLOWED_EXTENSIONS`, `UPLOAD_FOLDER`).
     - Pretrained model loading (Whisper + OpenVoice).
     - Audio processing & saving outputs to `OUTPUT_FOLDER`.
   - Optionally writes metadata to MongoDB (e.g., job records, audio paths).

2. **Web App – container 2**
   - Flask app (`app.py`) with:
     - `flask-login` for user authentication.
     - `User` model (`models.py`) with password hashing.
     - `auth` blueprint for registration/login/logout.
     - History stored in MongoDB (via `get_history_collection()`).
   - Responsibilities:
     - Serve the main UI (forms/pages).
     - Accept audio uploads and/or text input from users.
     - Call the ML client’s API endpoints to:
       - Transcribe/translate user audio.
       - Trigger voice cloning & TTS.
     - Store each user’s translation/voice-cloning history in MongoDB.
     - Render a dashboard of past translations and links to generated audio.

3. **Database – container 3**
   - MongoDB instance (official `mongo` image).
   - Stores:
     - `users` collection: username, hashed password, user metadata.
     - `history` (or similar) collection: per-user translation / voice-clone records.
   - The ML client and web app **share** this database.

**Communication**

- **Web app → MongoDB:** via `pymongo` in `db.py` / `get_history_collection`.
- **ML client → web app:** not needed directly.
- **Web app → ML client:** HTTP requests to ML API (internal Docker network).
- **ML client ↔ MongoDB (optional but recommended):** can log each processed job.

---