"""Registry functions for entities."""

import logging
from collections.abc import Callable

from domain.base.data.entities._collection_of_behaviors import CollectionOfBehaviors

logger = logging.getLogger(__name__)

_preset_registry: dict[str, type] = {}
_behavior_registry: dict[str, type] = {}


def register_preset(entity_name: str, preset_class: type):
    """Регистрирует класс пресета для сущности."""
    _preset_registry[entity_name] = preset_class
    logger.debug(f"Зарегистрирован пресет: {entity_name}")


def register_behavior(entity_name: str, behavior_class: Callable):
    """Регистрирует класс поведения для сущности."""
    _behavior_registry[entity_name] = behavior_class
    CollectionOfBehaviors.register_strategy(entity_name)(behavior_class)
    logger.debug(f"Зарегистрировано поведение: {entity_name}")


def get_preset(entity_name: str) -> type | None:
    """Возвращает класс пресета для сущности."""
    return _preset_registry.get(entity_name)


def get_behavior(entity_name: str) -> type | None:
    """Возвращает класс поведения для сущности."""
    return _behavior_registry.get(entity_name)


def get_all_presets() -> dict[str, type]:
    """Возвращает все зарегистрированные пресеты."""
    return _preset_registry.copy()


def get_all_behaviors() -> dict[str, type]:
    """Возвращает все зарегистрированные поведения."""
    return _behavior_registry.copy()
