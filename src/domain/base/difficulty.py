"""Система динамической сложности игры."""

import math
import random
from dataclasses import dataclass

from domain.base.difficulty_config import difficulty_config


@dataclass
class DifficultyProfile:
    """Профиль сложности для текущего уровня."""

    enemy_hp_multiplier: float = 1.0
    enemy_damage_multiplier: float = 1.0
    enemy_count_multiplier: float = 1.0
    item_quality_multiplier: float = 1.0
    elite_chance: float = 0.0
    boss_chance: float = 0.0

    def __post_init__(self):
        self.enemy_hp_multiplier = round(self.enemy_hp_multiplier, 2)
        self.enemy_damage_multiplier = round(self.enemy_damage_multiplier, 2)
        self.enemy_count_multiplier = round(self.enemy_count_multiplier, 2)
        self.item_quality_multiplier = round(self.item_quality_multiplier, 2)


class DifficultyCalculator:
    """Калькулятор сложности с учётом уровня и прокачки."""

    def __init__(self):
        self.base_enemy_hp = difficulty_config.get("base_values.enemy_hp", 50)
        self.base_enemy_damage = difficulty_config.get("base_values.enemy_damage", 10)
        self.max_enemy_multiplier = difficulty_config.get(
            "limits.max_hp_multiplier", 5.0
        )
        self.player_power_weights = difficulty_config.get("player_power_weights", {})
        self.max_stats = difficulty_config.get("max_stats", {})
        self.adaptive_enabled = difficulty_config.get(
            "adaptive_difficulty.enabled", True
        )
        self.player_power_influence = difficulty_config.get(
            "adaptive_difficulty.player_power_influence", 0.5
        )

    def calculate_difficulty(
        self, level_num: int, player_power: float, death_counter: int = 0
    ) -> DifficultyProfile:
        """Рассчитывает профиль сложности."""

        level_factor = 1.0 + (level_num - 1) * 0.08
        level_factor = min(level_factor, 3.0)

        if self.adaptive_enabled:
            player_factor = 1.0 + player_power * self.player_power_influence
            death_penalty = difficulty_config.get(
                "adaptive_difficulty.death_penalty", 0.1
            )
            player_factor = max(0.5, player_factor - death_counter * death_penalty)
        else:
            player_factor = 1.0

        total_multiplier = math.sqrt(level_factor * player_factor)
        total_multiplier = min(total_multiplier, self.max_enemy_multiplier)

        return DifficultyProfile(
            enemy_hp_multiplier=self._apply_growth_curve(total_multiplier, "enemy_hp"),
            enemy_damage_multiplier=self._apply_growth_curve(
                total_multiplier, "enemy_damage"
            ),
            enemy_count_multiplier=self._apply_growth_curve(
                total_multiplier, "enemy_count"
            ),
            item_quality_multiplier=self._apply_growth_curve(
                total_multiplier, "item_quality"
            ),
            elite_chance=difficulty_config.get_elite_chance(level_num),
            boss_chance=difficulty_config.get_boss_chance(level_num),
        )

    @staticmethod
    def _apply_growth_curve(multiplier: float, curve_type: str) -> float:
        """Применяет кривую роста к множителю."""
        curve_name = difficulty_config.get(f"difficulty_curves.{curve_type}", "linear")
        if curve_name == "logarithmic":
            result = 1.0 + math.log(multiplier)
        elif curve_name == "square_root":
            result = 1.0 + math.sqrt(multiplier - 1.0)
        elif curve_name == "logistic":
            result = 1.0 + (multiplier - 1.0) / (1.0 + math.exp(-(multiplier - 2.0)))
        else:
            result = multiplier
        limits = {
            "enemy_hp": "max_hp_multiplier",
            "enemy_damage": "max_damage_multiplier",
            "enemy_count": "max_count_multiplier",
        }
        if curve_type in limits:
            max_mult = difficulty_config.get(f"limits.{limits[curve_type]}", 5.0)
            result = min(result, max_mult)
        return round(result, 2)

    def calculate_player_power(self, player) -> float:
        """Рассчитывает силу игрока."""
        power = 0.0

        for stat, weight in self.player_power_weights.items():
            max_val = self.max_stats.get(stat, 100)

            if stat == "treasure" and hasattr(player, "backpack"):
                current_val = player.backpack.treasure
            else:
                current_val = getattr(player, stat, 0)

            if stat == "hp" and current_val == float("inf"):
                current_val = max_val * 0.5

            normalized = min(current_val / max_val, 1.0)
            power += normalized * weight

        return min(power, 1.0)

    @staticmethod
    def get_map_scale(level_num: int) -> float:
        """Возвращает масштаб карты."""
        return difficulty_config.get_map_scale(level_num)

    @staticmethod
    def calculate_treasure_reward(
        enemy, level_num: int, is_elite: bool = False, is_boss: bool = False
    ) -> int:
        """Рассчитывает награду за убийство врага."""
        config = difficulty_config.get("treasure_rewards", {})
        base_treasure = config.get("base_treasure", 10)
        elite_mult = config.get("elite_multiplier", 3)
        boss_mult = config.get("boss_multiplier", 5)
        level_scaling = config.get("level_scaling", 0.2)
        reward = base_treasure
        if hasattr(enemy, "strength"):
            strength_bonus = enemy.strength // 20
            reward += strength_bonus
        level_bonus = int(base_treasure * (level_num - 1) * level_scaling)
        reward += level_bonus
        if is_elite:
            reward *= elite_mult
        if is_boss:
            reward *= boss_mult

        random_bonus = random.uniform(0.8, 1.2)
        reward = int(reward * random_bonus)
        return max(1, reward)


difficulty_calculator = DifficultyCalculator()
