"""
Main entry point for the voice cloning translator ML client.
Orchestrates audio capture, transcription, translation, and voice cloning.
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from transcriber import WhisperTranscriber
from voice_cloner import VoiceCloner
from audio_recorder import AudioRecorder

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class VoiceCloningTranslator:

    def __init__(self, use_database: bool = None):
        """Initialize all components."""

        self.transcriber = WhisperTranscriber()
        self.voice_cloner = VoiceCloner()
        self.audio_recorder = AudioRecorder()

        # Default settings
        self.recording_duration = int(os.getenv("RECORDING_DURATION", "5"))

    def process_audio_file(self, audio_path: str) -> dict:
        logger.info(f"Processing audio file: {audio_path}")

        # Step 1: Translate audio to English using Whisper
        logger.info("Translating audio to English with Whisper...")
        translation_result = self.transcriber.translate_to_english(audio_path)
        english_text = translation_result["text"]
        source_language = translation_result["source_language"]
        logger.info(f"Source language: {source_language}")
        logger.info(f"English text: {english_text}")

        # Step 2: Clone voice and synthesize English speech
        logger.info("Cloning voice and synthesizing English speech...")
        output_audio_path = self.voice_cloner.clone_and_speak(
            reference_audio=audio_path,
            text=english_text,
            target_language="en",
        )
        logger.info(f"Output audio saved to: {output_audio_path}")

        # Step 3: Store results in database (if enabled)
        result = {
            "timestamp": datetime.utcnow(),
            "original_audio_path": audio_path,
            "source_language": source_language,
            "english_text": english_text,
            "output_audio_path": output_audio_path,
            "processing_time": translation_result.get("processing_time", 0),
        }

        if self.use_database and self.db_client:
            logger.info("Saving results to database...")
            result_id = self.db_client.save_translation_result(result)
            result["_id"] = result_id
            logger.info(f"Results saved with ID: {result_id}")
        else:
            logger.info("Database disabled, skipping save")

        return result

    def record_and_process(self, duration: int = None) -> dict:
        """
        Record audio from microphone and process it.

        Args:
            duration: Recording duration in seconds

        Returns:
            Dictionary containing processing results
        """
        if duration is None:
            duration = self.recording_duration

        logger.info(f"Recording audio for {duration} seconds...")
        audio_path = self.audio_recorder.record(duration=duration)
        logger.info(f"Audio recorded: {audio_path}")

        return self.process_audio_file(audio_path)

    def run_continuous(self, interval: int = 10):
        """
        Run continuous recording and processing loop.

        Args:
            interval: Time between recordings in seconds
        """
        logger.info("Starting continuous voice cloning translation...")
        logger.info(f"Recording every {interval} seconds")

        try:
            while True:
                try:
                    result = self.record_and_process()
                    logger.info(f"Processed: {result['original_text'][:50]}...")
                except Exception as e:
                    logger.error(f"Error processing audio: {e}")

                logger.info(f"Waiting {interval} seconds before next recording...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Stopping continuous processing...")

    def get_recent_translations(self, limit: int = 10) -> list:
        """
        Get recent translation results from database.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of translation results
        """
        return self.db_client.get_recent_translations(limit)


def main():
    """Main entry point."""
    logger.info("Initializing Voice Cloning Translator...")

    translator = VoiceCloningTranslator()

    # Check for command line arguments or environment variables
    mode = os.getenv("RUN_MODE", "continuous")

    if mode == "continuous":
        interval = int(os.getenv("RECORDING_INTERVAL", "30"))
        translator.run_continuous(interval=interval)
    elif mode == "single":
        audio_file = os.getenv("AUDIO_FILE")
        if audio_file:
            result = translator.process_audio_file(audio_file)
            logger.info(f"Processing complete: {result}")
        else:
            result = translator.record_and_process()
            logger.info(f"Recording and processing complete: {result}")
    else:
        logger.error(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main()
