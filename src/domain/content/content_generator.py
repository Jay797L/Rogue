import logging
import random
import uuid
from collections import deque
from collections.abc import Callable

from domain.base.core.character import Character
from domain.base.data.cell_presets import KeyCell, LockedDoorCell
from domain.base.data.colors import COLORS
from domain.base.data.item_presets import KeyItem
from domain.base.data.map_gen_prop import MapGenProp
from domain.base.difficulty import DifficultyProfile
from domain.base.utils.directions import ALL_DIRECTIONS
from domain.base.utils.point import Point
from domain.content.entity_fabric import (
    select_random_enemy,
)
from domain.content.item_fabric import select_random_item
from domain.map.level_generation.level import Level

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self, level: Level, props: MapGenProp, difficulty: int) -> None:
        self.level: Level = level
        self.enemies_at_level = props.enemies_at_level
        self.items_at_level = props.items_at_level
        self.difficulty_profile = None
        self.difficulty = difficulty

    def _apply_difficulty_to_enemy(
        self, enemy: Character, diff_profile: DifficultyProfile
    ) -> tuple[Character, bool, bool]:
        """
        Применяет модификаторы сложности к врагу.
        Возвращает (враг, is_elite, is_boss)
        """
        is_elite = False
        is_boss = False

        if not diff_profile:
            return enemy, is_elite, is_boss

        enemy.hp = int(enemy.hp * diff_profile.enemy_hp_multiplier)
        enemy.max_hp = enemy.hp

        enemy.strength = int(enemy.strength * diff_profile.enemy_damage_multiplier)

        if random.random() < diff_profile.elite_chance:
            is_elite = True
            enemy.name = f"Elite {enemy.name}"
            enemy.hp = int(enemy.hp * 1.5)
            enemy.strength = int(enemy.strength * 1.3)
            enemy.dexterity = int(enemy.dexterity * 1.2)
            if hasattr(enemy.cell, "color"):
                from domain.base.data.colors import COLORS

                enemy.cell.color = COLORS.RED

        if random.random() < diff_profile.boss_chance:
            is_boss = True
            enemy.name = f"Boss {enemy.name}"
            enemy.hp = int(enemy.hp * 2.5)
            enemy.strength = int(enemy.strength * 2.0)
            enemy.dexterity = int(enemy.dexterity * 1.5)
            if hasattr(enemy.cell, "color"):
                from domain.base.data.colors import COLORS

                enemy.cell.color = COLORS.MAGNETA

        return enemy, is_elite, is_boss

    def generate_entity(
        self,
        empty_points: list[Point],
        num_to_spawn: int,
        entity_selector: Callable[[], type],
        add_to_enemy_manager: bool = False,
    ) -> tuple[list[Point], int, list[tuple]]:
        """
        Универсальная функция для спавна сущностей.
        Возвращает (оставшиеся точки, количество спавнов, список информации о врагах)
        """
        remaining = empty_points.copy()
        spawned = 0
        count = min(num_to_spawn, len(remaining))
        enemies_info = []

        for _ in range(count):
            if not remaining:
                break
            point = remaining.pop()
            entity_class = entity_selector()
            if entity_class is None:
                logger.warning("entity_selector вернул None, пропускаем")
                continue
            entity = entity_class()

            is_elite = False
            is_boss = False
            if add_to_enemy_manager and self.difficulty_profile:
                entity, is_elite, is_boss = self._apply_difficulty_to_enemy(
                    entity, self.difficulty_profile
                )
                enemies_info.append((entity, is_elite, is_boss))

            self.level.entity_placer.place(entity, point)

            if add_to_enemy_manager:
                self.level.enemy_manager.add(entity)

            spawned += 1

        return remaining, spawned, enemies_info

    def _get_all_points_in_rect(
        self, y1: int, x1: int, y2: int, x2: int
    ) -> list[tuple[int, int]]:
        points = []
        min_y, max_y = min(y1, y2) + 1, max(y1, y2) - 1
        min_x, max_x = min(x1, x2) + 1, max(x1, x2) - 1
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                points.append((y, x))
        return points

    def generate_content(self, rooms_order: list[int]) -> None:

        for room_index in rooms_order:
            if room_index >= len(self.level.map_layout.rooms):
                continue

            room = self.level.map_layout.rooms[room_index]
            first_point, second_point = room.get_bound()

            all_points = self._get_all_points_in_rect(
                first_point.y, first_point.x, second_point.y, second_point.x
            )

            occupied_points = self.level.map_manager.get_non_empty_points_in_rect(
                first_point.y, first_point.x, second_point.y, second_point.x
            )

            occupied_set = set(occupied_points)
            empty_points = [
                Point(p[0], p[1]) for p in all_points if p not in occupied_set
            ]
            random.shuffle(empty_points)

            if not empty_points:
                continue

            num_enemies = random.randint(1, self.enemies_at_level)
            empty_points, _, enemies_info = self.generate_entity(
                empty_points,
                num_enemies,
                entity_selector=select_random_enemy,
                add_to_enemy_manager=True,
            )

            for enemy, is_elite, is_boss in enemies_info:
                if hasattr(self.level.enemy_manager, "enemies_info"):
                    self.level.enemy_manager.enemies_info[enemy.uid] = {
                        "is_elite": is_elite,
                        "is_boss": is_boss,
                        "level": self.difficulty,
                    }

            if empty_points:
                num_items = random.randint(1, self.items_at_level)
                self.generate_entity(
                    empty_points,
                    num_items,
                    entity_selector=select_random_item,
                    add_to_enemy_manager=False,
                )

    def _get_reachable_points(
        self, start: Point, blocked_points: set[Point]
    ) -> set[Point]:
        """BFS от start, не проходя через blocked_points."""
        visited = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            current = queue.popleft()
            for direction in ALL_DIRECTIONS:
                neighbor = current + direction
                if neighbor in visited or neighbor in blocked_points:
                    continue
                if self.level.map_manager.is_empty(neighbor):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    continue

        visited.discard(start)
        return visited

    def generate_locked_doors_and_keys(
        self, start_point: Point, exit_point: Point, num_pairs: int = 2
    ):
        """Генерирует закрытые двери и ключи."""
        if not self.level.map_layout.doors:
            logger.warning("No doors available for locking")
            return

        colors = [
            COLORS.RED,
            COLORS.BLUE,
            COLORS.GREEN,
            COLORS.YELLOW,
            COLORS.MAGNETA,
            COLORS.PERVANCHE,
        ]
        available_doors = list(self.level.map_layout.doors)
        random.shuffle(available_doors)
        selected_doors = available_doors[:num_pairs]

        used_key_points = set()

        for door_point in selected_doors:
            door_id = f"locked_door_{uuid.uuid4().hex[:8]}"
            color = random.choice(colors)

            locked_door = LockedDoorCell(door_id=door_id, color=color)
            self.level.map_manager[door_point] = locked_door
            self.level.map_layout.doors.remove(door_point)

            blocked = {door_point}
            reachable = self._get_reachable_points(start_point, blocked)
            reachable -= used_key_points
            reachable.discard(exit_point)

            if not reachable:
                logger.warning(
                    f"No reachable point for key to door {door_id}, reverting"
                )
                del self.level.map_manager[door_point]
                continue

            key_point = random.choice(list(reachable))
            used_key_points.add(key_point)

            key_item = KeyItem(opens_door_id=door_id)
            key_item.cell = KeyCell(color=color)
            key_item.cell.owner = key_item
            self.level.entity_placer.place(key_item, key_point)

            logger.info(
                f"Locked door {door_id} ({color.name}) at {door_point}, key at {key_point}"
            )
