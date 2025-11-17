"""
Whisper-based audio transcription module.
Uses OpenAI's Whisper model for speech-to-text conversion.
"""

import os
import time
import logging
import whisper

logger = logging.getLogger(__name__)


class WhisperTranscriber:

    def __init__(self, model_size: str = None):
        if model_size is None:
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")

        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.model_size = model_size
        logger.info(f"Whisper model {model_size} loaded successfully")

    def transcribe(self, audio_path: str, language: str = None) -> dict:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language code to force (e.g., 'en', 'es', 'fr')

        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected or specified language
                - segments: List of transcription segments with timestamps
                - processing_time: Time taken to process
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing audio file: {audio_path}")
        start_time = time.time()

        # Transcription options
        options = {
            "fp16": False,  # Use FP32 for better compatibility
            "verbose": False,
        }

        if language:
            options["language"] = language
            logger.info(f"Using specified language: {language}")

        # Perform transcription
        result = self.model.transcribe(audio_path, **options)

        processing_time = time.time() - start_time
        logger.info(f"Transcription completed in {processing_time:.2f} seconds")

        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "segments": result.get("segments", []),
            "processing_time": processing_time,
        }

    def translate_to_english(self, audio_path: str) -> dict:
        """
        Transcribe and translate any language audio to English text.

        Args:
            audio_path: Path to the audio file

        Returns:
            Dictionary containing:
                - text: Translated English text
                - source_language: Detected source language
                - segments: List of translation segments with timestamps
                - processing_time: Time taken to process
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Translating audio to English: {audio_path}")
        start_time = time.time()

        # Translation options - task="translate" converts any language to English
        options = {
            "task": "translate",
            "fp16": False,
            "verbose": False,
        }

        # Perform translation
        result = self.model.transcribe(audio_path, **options)

        processing_time = time.time() - start_time
        logger.info(f"Translation completed in {processing_time:.2f} seconds")

        return {
            "text": result["text"].strip(),
            "source_language": result["language"],
            "segments": result.get("segments", []),
            "processing_time": processing_time,
        }

    def detect_language(self, audio_path: str) -> str:
        """
        Detect the language of an audio file without full transcription.

        Args:
            audio_path: Path to the audio file

        Returns:
            Detected language code
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Detecting language for: {audio_path}")

        # Load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        # Make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # Detect the spoken language
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)

        logger.info(f"Detected language: {detected_lang}")
        return detected_lang

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_size": self.model_size,
            "device": str(self.model.device),
            "is_multilingual": self.model.is_multilingual,
        }
