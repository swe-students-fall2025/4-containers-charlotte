"""
Voice cloning module using OpenVoice.
Clones speaker characteristics and synthesizes speech in the cloned voice.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# OpenVoice imports - these will be available when OpenVoice is installed
try:
    import torch
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS

    OPENVOICE_AVAILABLE = True
except ImportError:
    OPENVOICE_AVAILABLE = False
    logger.warning("OpenVoice not available. Voice cloning will use mock implementation.")


class VoiceCloner:

    def __init__(self):
        """Initialize the voice cloner."""
        self.output_dir = os.getenv("OUTPUT_AUDIO_DIR", "/tmp/voice_output")
        os.makedirs(self.output_dir, exist_ok=True)

        if OPENVOICE_AVAILABLE:
            self._init_openvoice()
        else:
            logger.warning("Running in mock mode - no actual voice cloning")

    def _init_openvoice(self):
        logger.info("Initializing OpenVoice models...")

        # Device configuration
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Load tone color converter
        ckpt_converter = os.getenv(
            "OPENVOICE_CONVERTER_CKPT", "checkpoints_v2/converter"
        )

        if os.path.exists(ckpt_converter):
            self.tone_color_converter = ToneColorConverter(
                f"{ckpt_converter}/config.json", device=self.device
            )
            self.tone_color_converter.load_ckpt(f"{ckpt_converter}/checkpoint.pth")
            logger.info("Tone color converter loaded")
        else:
            logger.warning(f"Converter checkpoint not found at {ckpt_converter}")
            self.tone_color_converter = None

        # Initialize TTS for base speaker
        self.tts_model = TTS(language="EN", device=self.device)
        self.speaker_ids = self.tts_model.hps.data.spk2id

        logger.info("OpenVoice initialization complete")

    def clone_and_speak(
        self, reference_audio: str, text: str, target_language: str = "en"
    ) -> str:
        '''
        Clone voice from reference audio and synthesize text in that voice.

        Args:
            reference_audio: Path to reference audio file for voice cloning
            text: Text to synthesize
            target_language: Target language code

        Returns:
            Path to the output audio file
        '''
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        logger.info(f"Cloning voice from: {reference_audio}")
        logger.info(f"Text to synthesize: {text}")

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.output_dir, f"cloned_voice_{timestamp}.wav"
        )

        if OPENVOICE_AVAILABLE and self.tone_color_converter:
            output_path = self._clone_with_openvoice(
                reference_audio, text, target_language, output_path
            )
        else:
            output_path = self._mock_clone(text, output_path)

        logger.info(f"Output audio saved to: {output_path}")
        return output_path

    def _clone_with_openvoice(
        self, reference_audio: str, text: str, target_language: str, output_path: str
    ) -> str:
        '''
        Perform actual voice cloning with OpenVoice.

        Args:
            reference_audio: Path to reference audio
            text: Text to synthesize
            target_language: Target language
            output_path: Path for output file

        Returns:
            Path to output audio file
        '''
        # Extract speaker embedding from reference audio
        logger.info("Extracting speaker embedding...")
        target_se, _ = se_extractor.get_se(
            reference_audio, self.tone_color_converter, vad=False
        )

        # Generate base TTS audio
        logger.info("Generating base TTS audio...")
        src_path = output_path.replace(".wav", "_src.wav")

        # Map language code to OpenVoice language
        language_map = {
            "en": "EN",
            "es": "ES",
            "fr": "FR",
            "zh": "ZH",
            "ja": "JP",
            "ko": "KR",
        }
        tts_lang = language_map.get(target_language, "EN")

        # Reinitialize TTS if language changed
        if tts_lang != "EN":
            self.tts_model = TTS(language=tts_lang, device=self.device)

        speaker_key = list(self.tts_model.hps.data.spk2id.keys())[0]
        speaker_id = self.tts_model.hps.data.spk2id[speaker_key]

        self.tts_model.tts_to_file(text, speaker_id, src_path, speed=1.0)

        # Extract source speaker embedding
        source_se = torch.load(
            os.path.join(
                os.getenv("OPENVOICE_CONVERTER_CKPT", "checkpoints_v2/converter"),
                "base_speakers/ses/base.pth",
            ),
            map_location=self.device,
        )

        # Apply voice conversion
        logger.info("Applying voice conversion...")
        self.tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path,
        )

        # Clean up temporary file
        if os.path.exists(src_path):
            os.remove(src_path)

        return output_path

    def _mock_clone(self, text: str, output_path: str) -> str:
        # Create a placeholder audio file
        # In production, this would be actual synthesized audio
        with open(output_path, "wb") as f:
            # Write minimal WAV header for a silent audio file
            # This is just for testing purposes
            f.write(self._create_silent_wav())

        return output_path

    def get_supported_languages(self) -> list:
        return ["en", "es", "fr", "zh", "ja", "ko"]

    def is_available(self) -> bool:
        return OPENVOICE_AVAILABLE
