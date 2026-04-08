from domain.base.core.character import Character
from domain.base.core.effect import Effect
from domain.base.data.strings import STRINGS
from domain.base.difficulty import difficulty_calculator
from domain.base.utils.point import Point
from domain.entity_logic.behavior_enforcer import BehaviorEnforcer
from domain.map.map_assembly.map_manager import MapManager


class EnemyManager:
    def __init__(self, map_manager: MapManager, behavior_enforcer: BehaviorEnforcer):
        self.enemies: list[Character] = []
        self.behavior_enforcer = behavior_enforcer
        self.active_effects: list[Effect] = []
        self.map_manager = map_manager
        self.enemies_info: dict = {}  # Храним информацию о врагах
        self.current_level = 1  # Текущий уровень сложности

    def add(self, entity, is_elite: bool = False, is_boss: bool = False):
        """Добавляет врага с информацией о его типе."""
        if entity not in self.enemies:
            self.enemies.append(entity)
            self.enemies_info[entity.uid] = {
                "is_elite": is_elite,
                "is_boss": is_boss,
                "level": self.current_level,
            }

    def update(self, game=None):
        for enemy in self.enemies:
            effects_from_enemy = self.behavior_enforcer.perform_live_tick(enemy)
            for effect in effects_from_enemy:
                self.active_effects.append(effect)

        # Применяем эффекты и удаляем мёртвых с передачей game
        self._apply_effects_and_remove_dead(game)

    def _apply_effects_and_remove_dead(self, game=None):
        # Применяем эффекты
        for effect in self.active_effects:
            effect.apply()

        # Удаляем мёртвых врагов с начислением награды
        self._remove_dead_enemies(game)

        # Убираем отработанные эффекты
        self.active_effects = [e for e in self.active_effects if not e.its_time_to_die]

    def _remove_dead_enemies(self, game=None):
        """Удаляет врагов с hp <= 0 с карты и из списка, начисляет награду."""
        dead = [e for e in self.enemies if e.hp <= 0]
        for enemy in dead:
            # Начисляем сокровища за убийство
            if game:
                self._award_treasure_for_kill(enemy, game)

            if self.map_manager and enemy.point in self.map_manager:
                cell = self.map_manager[enemy.point]
                if cell and hasattr(cell, "owner"):
                    cell.owner = None
                del self.map_manager[enemy.point]

            # Удаляем информацию о враге
            if enemy.uid in self.enemies_info:
                del self.enemies_info[enemy.uid]

            self.enemies.remove(enemy)
        return dead

    def _award_treasure_for_kill(self, enemy, game):
        """Начисляет сокровища за убийство врага."""

        # Получаем информацию о враге
        enemy_info = self.enemies_info.get(enemy.uid, {})
        is_elite = enemy_info.get("is_elite", False)
        is_boss = enemy_info.get("is_boss", False)
        level_num = enemy_info.get("level", game.current_level_num if game else 1)

        # Рассчитываем награду
        reward = difficulty_calculator.calculate_treasure_reward(
            enemy, level_num, is_elite, is_boss
        )

        # Начисляем сокровища игроку
        game.player.backpack.treasure += reward

        # Записываем статистику
        game.record_treasure(reward)

        # Сообщение игроку
        if is_boss:
            enemy_type = STRINGS.BOSS_PREFIX
        elif is_elite:
            enemy_type = STRINGS.ELITE_PREFIX
        else:
            enemy_type = STRINGS.ENEMY_TYPE_ENEMY

        game.message = STRINGS.TREASURE_REWARD.format(
            reward, enemy_type.value, enemy.name
        )

    def player_desision(self, direction: Point):
        effects_from_player = self.behavior_enforcer.perform_player_behavior(direction)
        self.active_effects.extend(effects_from_player)

    def effects_apply(self):
        # 1. Применяем все эффекты
        for effect in self.active_effects:
            effect.apply()

        # 2. Удаляем мёртвых врагов (без колбэка)
        self._remove_dead_enemies()

        # 3. Убираем отработанные эффекты
        self.active_effects = [e for e in self.active_effects if not e.its_time_to_die]

    def max_hp_check(self, player):
        for enemy in self.enemies:
            enemy.hp = min(enemy.hp, enemy.max_hp)
        player.hp = min(player.hp, player.max_hp)
