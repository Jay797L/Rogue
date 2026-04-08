import importlib
import logging
from pathlib import Path

from ._registry import (
    get_all_behaviors,
    get_all_presets,
    get_behavior,
    get_preset,
    register_behavior,
    register_preset,
)
from .ghost import Ghost
from .mimik import Mimik
from .ogr import Ogr
from .player import Player
from .snake_mage import SnakeMage
from .vampire import Vampire
from .zombie import Zombie

logger = logging.getLogger(__name__)

_imported = False


def _import_all_patterns():
    global _imported
    if _imported:
        return
    _imported = True

    package_dir = Path(__file__).parent
    package_name = __name__

    for entry in package_dir.iterdir():
        name = entry.name
        if name.startswith("_"):
            continue

        if not entry.is_file() or entry.suffix != ".py":
            continue
        stem = entry.stem
        if stem not in {"__init__", "_registry", "_export", "_import"}:
            module_name = f"{package_name}.{stem}"
            try:
                importlib.import_module(module_name)
                logger.info(f"Загружен модуль сущности: {stem}")
            except Exception as e:
                logger.exception(e)


def register_all_patterns():
    """Принудительная регистрация всех паттернов."""
    _import_all_patterns()


__all__ = [
    "register_preset",
    "register_behavior",
    "get_preset",
    "get_behavior",
    "get_all_presets",
    "get_all_behaviors",
    "register_all_patterns",
    "Ghost",
    "Mimik",
    "Ogr",
    "Player",
    "SnakeMage",
    "Vampire",
    "Zombie",
]
