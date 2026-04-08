from . import (
    cell_presets,
    consts,
    entities,
    item_presets,
)
from .colors import COLORS
from .entities import (
    Ghost,
    Mimik,
    Ogr,
    Player,
    SnakeMage,
    Vampire,
    Zombie,
    get_all_behaviors,
    get_all_presets,
    get_behavior,
    get_preset,
    register_all_patterns,
    register_behavior,
    register_preset,
)
from .graph_masks import MASKS
from .map_gen_prop import MapGenProp
from .register_item import get_all_items, get_item_by_name, get_items_by_category
from .strings import STRINGS

__all__ = [
    "cell_presets",
    "consts",
    "entities",
    "item_presets",
    "COLORS",
    "STRINGS",
    "MASKS",
    "MapGenProp",
    "get_items_by_category",
    "get_all_items",
    "get_item_by_name",
    "Ghost",
    "Ogr",
    "Player",
    "SnakeMage",
    "Vampire",
    "Zombie",
    "Mimik",
    "register_preset",
    "register_behavior",
    "get_preset",
    "get_behavior",
    "get_all_presets",
    "get_all_behaviors",
    "register_all_patterns",
]

from domain.base.data.item_presets import register_all_items

register_all_items()
