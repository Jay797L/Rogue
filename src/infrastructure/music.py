"""Music player module for background music."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("Pygame not installed. Music playback disabled.")


class MusicPlayer:
    """Simple music player for background music."""

    def __init__(self, music_path: Path | str):
        """
        Initialize the music player.

        Args:
            music_path: Path to the music file (mp3).
        """
        self.music_path = Path(music_path)
        self._initialized = False
        self._playing = False

        if not PYGAME_AVAILABLE:
            logger.info("Pygame not available, music disabled")
            return

        self._init_pygame()

    def _init_pygame(self) -> None:
        """Initialize pygame mixer."""
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._initialized = True
            logger.info("Pygame mixer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            self._initialized = False

    def play(self, loops: int = -1) -> bool:
        """
        Start playing music.

        Args:
            loops: Number of loops (-1 for infinite)

        Returns:
            True if playback started successfully, False otherwise
        """
        if not self._initialized or not PYGAME_AVAILABLE:
            return False

        if not self.music_path.exists():
            logger.warning(f"Music file not found: {self.music_path}")
            return False

        try:
            pygame.mixer.music.load(str(self.music_path))
            pygame.mixer.music.play(loops)
            self._playing = True
            logger.info(f"Playing music: {self.music_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to play music: {e}")
            return False

    def stop(self) -> None:
        """Stop playing music."""
        if not self._initialized or not PYGAME_AVAILABLE:
            return

        try:
            pygame.mixer.music.stop()
            self._playing = False
            logger.info("Music stopped")
        except Exception as e:
            logger.error(f"Failed to stop music: {e}")

    def pause(self) -> None:
        """Pause music playback."""
        if not self._initialized or not PYGAME_AVAILABLE:
            return

        try:
            pygame.mixer.music.pause()
            self._playing = False
            logger.info("Music paused")
        except Exception as e:
            logger.error(f"Failed to pause music: {e}")

    def unpause(self) -> None:
        """Unpause music playback."""
        if not self._initialized or not PYGAME_AVAILABLE:
            return

        try:
            pygame.mixer.music.unpause()
            self._playing = True
            logger.info("Music unpaused")
        except Exception as e:
            logger.error(f"Failed to unpause music: {e}")

    @property
    def is_playing(self) -> bool:
        """Return whether music is currently playing."""
        if not self._initialized or not PYGAME_AVAILABLE:
            return False

        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return self._playing

    def set_volume(self, volume: float) -> None:
        """
        Set music volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self._initialized or not PYGAME_AVAILABLE:
            return

        try:
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            logger.debug(f"Music volume set to {volume}")
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
