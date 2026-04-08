import random

from domain.base.core.character import Character
from domain.base.data.consts import CONST
from domain.base.data.entities import get_all_presets


def select_random_enemy() -> type[Character]:
    """
    Выбирает случайного врага с учётом весовых коэффициентов по типам.

    Веса (пример):
    - zombie: 40%
    - ghost: 25%
    - ogr: 20%
    - snake_mage: 10%
    - vampire: 5%
    - mimik: 0%
    """
    type_weights = {
        "Zombie": 35,
        "Ghost": 20,
        "Ogr": 15,
        "Snake_mage": 10,
        "Vampire": 5,
        "Mimik": 15,
    }
    presets: dict = get_all_presets()
    available_types = []
    weights = []
    for enemy_type, weight in type_weights.items():
        if enemy_type in presets and weight > 0:
            available_types.append(enemy_type)
            weights.append(weight)

    if not available_types:
        all_enemies = list(presets.values())
        return random.choice(all_enemies) if all_enemies else None

    selected_type = random.choices(available_types, weights=weights, k=1)[0]
    enemies = presets[selected_type]
    return enemies


def select_random_enemy_with_level(
    level_num: int, diff_profile=None
) -> type[Character]:
    """
    Выбирает случайного врага с учётом уровня сложности.
    Используется для динамической сложности.

    Args:
        level_num: Номер уровня
        diff_profile: Профиль сложности (опционально)

    Returns:
        Класс врага
    """

    weights = {
        "zombie": 35,
        "ghost": 20,
        "ogr": 15,
        "snake_mage": 10,
        "vampire": 5,
        "mimik": 15,
    }

    if level_num >= CONST.EARLY_ELITE_THRESHOLD:
        weights["ogr"] += 10
        weights["snake_mage"] += 5
    if level_num >= CONST.MID_ELITE_THRESHOLD:
        weights["vampire"] += 15
        weights["snake_mage"] += 10
    if level_num >= CONST.HIGH_ELITE_THRESHOLD:
        weights["mimik"] = 10

    if (
        diff_profile
        and hasattr(diff_profile, "elite_chance")
        and diff_profile.elite_chance > 0
    ):
        for key in weights:
            weights[key] = int(weights[key] * (1 + diff_profile.elite_chance))

    presets = get_all_presets()
    available_types = []
    weight_list = []

    for enemy_type, weight in weights.items():
        if enemy_type in presets and weight > 0:
            available_types.append(enemy_type)
            weight_list.append(weight)

    if not available_types:
        all_enemies = list(presets.values())
        return random.choice(all_enemies) if all_enemies else None

    selected_type = random.choices(available_types, weights=weight_list, k=1)[0]
    enemies = presets[selected_type]
    return random.choice(enemies)
