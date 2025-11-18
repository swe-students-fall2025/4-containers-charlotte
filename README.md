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
Prerequisites

Git

Docker & Docker Compose
(Docker Desktop on macOS/Windows; Docker Engine + Compose on Linux)

Python 3.10+ if you want to run things locally (outside of Docker)

pip or pipenv

Enough disk space to host Whisper + OpenVoice model weights

Model installation (high level):

Install Whisper (e.g. openai-whisper or equivalent).

Install OpenVoice and ensure models/checkpoints are either:

downloaded at container build time, or

mounted as a volume into the ML container.

Exact install details live in machine-learning-client/requirements.txt and Dockerfile.
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