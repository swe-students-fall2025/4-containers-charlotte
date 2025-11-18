'''
TTS-based voice cloning model
'''

import os
import logging
from datetime import datetime
import torch
from TTS.api import TTS
from app.config import Config

logger = logging.getLogger(__name__)


class VoiceCloner:
    '''
    Voice cloning using Coqui TTS.

    Provides text-to-speech synthesis with voice cloning capabilities.
    Can clone a voice from a reference audio sample and synthesize
    new speech in that voice.

    Attributes
    ----------
    output_dir : str
        Directory for saving generated audio files.
    tts_model : TTS or None
        Loaded TTS model instance, or None if unavailable.
    device : str or None
        Device being used ('cpu' or 'cuda'), or None if unavailable.
    '''

    def __init__(self):
        '''
        Initialize voice cloner.

        Creates output directory and loads TTS model if available.
        Falls back to mock mode if TTS library is not installed.
        '''
        self.output_dir = Config.OUTPUT_FOLDER
        os.makedirs(self.output_dir, exist_ok=True)

        self.tts_model = None
        self.device = None

        if TTS is not None:
            self._init_model()
        else:
            logger.error('Running in mock mode - no actual voice cloning')

    def _init_model(self):
        '''
        Initialize TTS model.

        Sets up the device (CPU/GPU) and loads the TTS model.
        Falls back to None if initialization fails.
        '''
        logger.info('Initializing TTS model...')

        # Device configuration
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'Using device: {self.device}')

        try:
            # Initialize TTS with a multilingual model
            self.tts_model = TTS(
                model_name='tts_models/multilingual/multi-dataset/your_tts',
                progress_bar=False
            ).to(self.device)

            logger.info('TTS model initialization complete')
        except Exception as e:
            logger.error(f'Failed to initialize TTS model: {e}')
            self.tts_model = None

    def clone_and_speak(self, reference_audio, text, target_language='en'):
        '''
        Clone voice from reference audio and synthesize text in that voice.

        Parameters
        ----------
        reference_audio : str
            Path to reference audio file for voice cloning.
        text : str
            Text to synthesize.
        target_language : str, default='en'
            Target language code for synthesis ('en', 'es', 'fr', etc.).

        Returns
        -------
        output_path : str
            Path to the generated audio file.

        Raises
        ------
        ValueError
            If text is empty.
        FileNotFoundError
            If reference audio file does not exist.
        '''
        if not text or not text.strip():
            raise ValueError('Text cannot be empty')

        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f'Reference audio not found: {reference_audio}')

        logger.info(f'Cloning voice from: {reference_audio}')
        logger.info(f'Text to synthesize: {text[:50]}...')

        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            self.output_dir, f'cloned_voice_{timestamp}.wav'
        )

        if self.tts_model is not None:
            output_path = self._clone_with_tts(
                reference_audio, text, target_language, output_path
            )
        else:
            output_path = self._mock_clone(output_path)

        logger.info(f'Output audio saved to: {output_path}')
        return output_path

    def _clone_with_tts(self, reference_audio, text, target_language, output_path):
        '''
        Perform actual voice cloning with TTS.

        Parameters
        ----------
        reference_audio : str
            Path to reference audio.
        text : str
            Text to synthesize.
        target_language : str
            Target language.
        output_path : str
            Path for output file.

        Returns
        -------
        output_path : str
            Path to output audio file.
        '''
        try:
            logger.info('Generating cloned voice...')

            # Generate speech with voice cloning
            self.tts_model.tts_to_file(
                text=text,
                speaker_wav=reference_audio,
                language=target_language,
                file_path=output_path
            )

            logger.info('Voice cloning completed successfully')
            return output_path

        except Exception as e:
            logger.error(f'Voice cloning failed: {e}')
            logger.warning('Falling back to mock mode')
            return self._mock_clone(output_path)

    def _mock_clone(self, output_path):
        '''
        Create a placeholder audio file for testing.

        Parameters
        ----------
        output_path : str
            Path for output file.

        Returns
        -------
        output_path : str
            Path to output audio file.
        '''
        logger.info('Creating mock audio file')

        # Just create an empty file as placeholder
        with open(output_path, 'wb') as f:
            f.write(b'')

        return output_path

    def is_available(self):
        '''
        Check if voice cloning is available.

        Returns
        -------
        available : bool
            True if TTS model is loaded, False otherwise.
        '''
        return self.tts_model is not None

    def get_model_info(self):
        '''
        Get information about the TTS model.

        Returns
        -------
        info : dict
            Dictionary with model information:
            - available : bool
                Whether voice cloning is available
            - device : str or None
                Device being used
            - model_loaded : bool
                Whether model is successfully loaded
        '''
        if self.tts_model is not None:
            return {
                'available': True,
                'device': self.device,
                'model_loaded': True
            }
        return {
            'available': False,
            'device': None,
            'model_loaded': False
        }
