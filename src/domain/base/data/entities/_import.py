import random
from dataclasses import dataclass, field
from itertools import cycle, islice
from pathlib import Path

from domain.base.core.cell import Cell
from domain.base.core.character import Character, check_status_in_character
from domain.base.core.effect import Effect
from domain.base.data.colors import COLORS
from domain.base.data.entities._collection_of_behaviors import (
    CollectionOfBehaviors,
)
from domain.base.utils.directions import ALL_DIRECTIONS
from domain.base.utils.point import Point
from domain.game.core.entity_logic.combat import Attack, Heal, StunEffect
from domain.game.core.entity_logic.move_order import MoveOrder
from domain.map.map_assembly.map_manager import MapManager

__all__ = [
    "check_status_in_character",
    "random",
    "dataclass",
    "field",
    "cycle",
    "islice",
    "Path",
    "Cell",
    "Character",
    "Effect",
    "ALL_DIRECTIONS",
    "COLORS",
    "Point",
    "CollectionOfBehaviors",
    "Attack",
    "Heal",
    "StunEffect",
    "MoveOrder",
    "MapManager",
]
