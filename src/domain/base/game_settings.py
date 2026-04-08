"""Module for managing game settings."""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GameSettings:
    """Game settings."""

    music_enabled: bool = True

    def to_dict(self) -> dict:
        """Convert to dict for JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameSettings":
        """Create from dict."""
        return cls(**data)


class SettingsManager:
    """Settings manager that persists to a JSON file."""

    SETTINGS_FILENAME = "data/repos/settings.json"

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.settings_path = self.project_root / self.SETTINGS_FILENAME
        self.settings = GameSettings()
        self._load()

    def _load(self) -> None:
        """Load settings from file."""
        if not self.settings_path.exists():
            logger.info(
                f"Settings file not found, using defaults: {self.settings_path}"
            )
            return

        try:
            with open(self.settings_path, encoding="utf-8") as f:
                data = json.load(f)
            self.settings = GameSettings.from_dict(data)
            logger.info(f"Settings loaded from {self.settings_path}")
        except Exception as e:
            logger.error("Failed to load settings: {}", e)

    def save(self) -> None:
        """Save settings to file."""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info("Settings saved to {}", self.settings_path)
        except Exception as e:
            logger.error("Failed to save settings: {}", e)

    def set_music_enabled(self, enabled: bool) -> None:
        """Set music enabled state and save."""
        self.settings.music_enabled = enabled
        self.save()

    def get_music_enabled(self) -> bool:
        """Return music enabled state."""
        return self.settings.music_enabled
