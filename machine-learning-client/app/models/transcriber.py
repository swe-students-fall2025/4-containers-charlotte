"""
Audio transcription model
"""

import logging
import os
import time
from typing import Dict, Optional

import whisper

from app.config import Config

logger = logging.getLogger(__name__)


class Transcriber:
    """
    Audio transcription using OpenAI Whisper model.

    Provides methods for transcribing audio files, translating to English,
    and detecting languages using the Whisper speech recognition model.

    Attributes
    ----------
    model : whisper.model.Whisper
        Loaded Whisper model instance.
    model_size : str
        Size of the loaded model (tiny, base, small, medium, large).
    """

    def __init__(self, model_size: Optional[str] = None):
        """
        Initialize Whisper transcriber.

        Parameters
        ----------
        model_size : str, optional
            Whisper model size ('tiny', 'base', 'small', 'medium', 'large').
            If None, defaults to value from config.
        """
        if model_size is None:
            model_size = Config.TRANSCRIBER_MODEL_SIZE

        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.model_size = model_size
        logger.info(f"Whisper model {model_size} loaded successfully")

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """
        Transcribe an audio file to text.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.
        language : str, optional
            Language code ('en', 'fr', 'ko', 'zh').
            If None, language will be auto-detected.

        Returns
        -------
        result : dict
            Dictionary containing transcription results:
            - text : str
                Transcribed text
            - language : str
                Detected or specified language
            - segments : list
                List of transcription segments with timestamps
            - processing_time : float
                Time taken to process in seconds

        Raises
        ------
        FileNotFoundError
            If audio file does not exist.
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

    def translate_to_english(self, audio_path: str) -> Dict:
        """
        Transcribe and translate any language audio to English text.

        Uses Whisper's built-in translation capability to convert
        audio in any language to English text.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        result : dict
            Dictionary containing translation results:
            - text : str
                Translated English text
            - source_language : str
                Detected source language
            - segments : list
                List of translation segments with timestamps
            - processing_time : float
                Time taken to process in seconds

        Raises
        ------
        FileNotFoundError
            If audio file does not exist.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Translating audio to English: {audio_path}")
        start_time = time.time()

        # Translation options - task='translate' converts any language to English
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

        Uses the first 30 seconds of audio to detect the spoken language.
        This is faster than full transcription when only language
        identification is needed.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        language : str
            Detected language code (e.g., 'en', 'fr', 'es', 'ko').

        Raises
        ------
        FileNotFoundError
            If audio file does not exist.
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

        logger.info(
            f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})"
        )
        return detected_lang

    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.

        Returns
        -------
        info : dict
            Dictionary with model information:
            - model_size : str
                Size of the loaded model
            - device : str
                Device being used (cpu or cuda)
            - is_multilingual : bool
                Whether model supports multiple languages
        """
        return {
            "model_size": self.model_size,
            "device": str(self.model.device),
            "is_multilingual": self.model.is_multilingual,
        }
