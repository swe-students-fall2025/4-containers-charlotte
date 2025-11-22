"""
Audio processor logic
"""

import os
import logging
from datetime import datetime
from app.db import gridfs
from app.models.transcriber import Transcriber
from app.models.voice_cloner import VoiceCloner

logger = logging.getLogger(__name__)


class Processor:
    """
    Service for audio processing operations.

    Combines transcription and voice cloning functionality.
    """

    def __init__(self):
        self.transcriber = Transcriber()
        self.voice_cloner = VoiceCloner()
        logger.info("AudioProcessor initialized")

    def transcribe(self, audio_path, language=None):
        """
        Transcribe audio to text.

        Parameters
        ----------
        audio_path : str
            Path to audio file.
        language : str, optional
            Optional language code ('en', 'fr', 'kr', 'zh').
            If None, language will be auto-detected.

        Returns
        -------
        result : dict
            Dictionary with transcription results containing:
            - text : str
                Transcribed text
            - language : str
                Detected or specified language
            - segments : list
                List of transcription segments with timestamps
            - processing_time : float
                Time taken to process in seconds
            - timestamp : str
                ISO format timestamp of processing
            - audio_path : str
                Path to the processed audio file
        """
        logger.info(f"Transcribing audio: {audio_path}")
        result = self.transcriber.transcribe(audio_path, language)
        result["timestamp"] = datetime.utcnow().isoformat()
        result["audio_path"] = audio_path
        return result

    def translate_to_english(self, audio_path):
        """
        Translate audio to English.

        Parameters
        ----------
        audio_path : str
            Path to audio file.

        Returns
        -------
        result : dict
            Dictionary with translation results containing:
            - text : str
                Translated English text
            - source_language : str
                Detected source language
            - segments : list
                List of translation segments with timestamps
            - processing_time : float
                Time taken to process in seconds
            - timestamp : str
                ISO format timestamp of processing
            - audio_path : str
                Path to the processed audio file
        """
        logger.info(f"Translating audio: {audio_path}")
        result = self.transcriber.translate_to_english(audio_path)
        result["timestamp"] = datetime.utcnow().isoformat()
        result["audio_path"] = audio_path
        return result

    def clone_voice(self, reference_audio, text, target_language="en"):
        """
        Clone voice and synthesize speech.

        Parameters
        ----------
        reference_audio : str
            Path to reference audio file for voice cloning.
        text : str
            Text to synthesize.
        target_language : str, default='en'
            Target language code for synthesis.

        Returns
        -------
        output_path : str
            Path to the generated audio file.
        """
        logger.info(f"Cloning voice from: {reference_audio}")
        output_path = self.voice_cloner.clone_and_speak(
            reference_audio, text, target_language
        )
        return output_path

    def process_audio_file(self, audio_path):
        """
        Complete workflow: translate and clone voice.

        This method performs a complete audio processing pipeline:
        1. Translates the audio to English text
        2. Clones the original voice with the translated text
        3. Uploads the output audio to GridFS

        Parameters
        ----------
        audio_path : str
            Path to input audio file.

        Returns
        -------
        result : dict
            Dictionary with complete processing results containing:
            - timestamp : str
                ISO format timestamp of processing
            - original_audio_path : str
                Path to original audio file
            - source_language : str
                Detected source language
            - english_text : str
                Translated English text
            - output_file_id : str
                ObjectId of the generated audio file in GridFS
            - processing_time : float
                Total processing time in seconds
        """
        logger.info(f"Processing audio file: {audio_path}")

        # Step 1: Translate to English
        translation_result = self.translate_to_english(audio_path)
        english_text = translation_result["text"]
        source_language = translation_result["source_language"]

        # Step 2: Clone voice
        output_audio_path = self.clone_voice(
            reference_audio=audio_path, text=english_text, target_language="en"
        )

        # Step 3: Upload output audio to GridFS
        output_filename = os.path.basename(output_audio_path)
        with open(output_audio_path, "rb") as audio_file:
            file_id = gridfs.upload_from_stream(
                output_filename,
                audio_file,
                metadata={
                    "source_language": source_language,
                    "english_text": english_text,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        os.remove(output_audio_path)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "original_audio_path": audio_path,
            "source_language": source_language,
            "english_text": english_text,
            "output_file_id": str(file_id),
            "processing_time": translation_result.get("processing_time", 0),
        }

        return result
