"""Генератор уровней."""

import logging
import random
import time
from typing import Any

from domain.base.core.entity import Entity
from domain.base.data import Player
from domain.base.data.cell_presets import ExitCell, LockedDoorCell
from domain.base.data.map_gen_prop import MapGenProp
from domain.base.data.strings import STRINGS
from domain.base.difficulty import difficulty_calculator
from domain.base.utils.point import Point
from domain.content.content_generator import ContentGenerator
from domain.game.core.entity_logic.behavior_enforcer import BehaviorEnforcer
from domain.game.core.entity_logic.enemy_manager import EnemyManager
from domain.game.core.entity_logic.entity_placement import EntityPlacer
from domain.map.level_generation.level import Level
from domain.map.map_assembly.map_generator import MapGenerator
from domain.vision.ray_caster import RaycastingVisibility

logger = logging.getLogger(__name__)


class LevelGenerator:
    """Генератор уровней игры."""

    @staticmethod
    def level_gen(
        player: Player,
        difficulty: int = 1,
        seed: int | None = None,
        opened_doors: list[Any] | None = None,
        player_start_point: Point | None = None,
        retries: int = 3,
    ) -> Level | None:
        """Генерирует уровень с динамической сложностью.

        Args:
            player: Игрок
            difficulty: Уровень сложности
            seed: Сид для генерации
            opened_doors: Список открытых дверей
            player_start_point: Точка старта игрока (если None - генерируется случайно)
            retries: Количество попыток при сбое генерации
        """
        for attempt in range(retries):
            try:
                if seed is None:
                    current_seed = int(time.time())
                else:
                    current_seed = seed

                player_power = difficulty_calculator.calculate_player_power(player)
                diff_profile = difficulty_calculator.calculate_difficulty(
                    difficulty, player_power
                )
                map_scale = difficulty_calculator.get_map_scale(difficulty)

                logger.info(
                    f"Generating level (attempt {attempt + 1}/{retries}): difficulty={difficulty}, seed={current_seed}, map_scale={map_scale}"
                )
                logger.info(f"Player power={player_power}, diff_profile={diff_profile}")

                prop = MapGenProp(
                    seed=current_seed,
                    map_scale=map_scale,
                    enemies_at_level=max(
                        1, int(3 * diff_profile.enemy_count_multiplier)
                    ),
                    items_at_level=max(
                        1, int(2 * diff_profile.item_quality_multiplier)
                    ),
                )

                logger.info(
                    f"MapGenProp created: min_room_height={prop.min_room_height}, min_room_width={prop.min_room_width}"
                )

                map_layout, map_manager = MapGenerator.generate_map(prop)

                if map_layout is None:
                    logger.error("map_layout is None")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                rooms_count = len(map_layout.rooms) if map_layout.rooms else 0
                logger.info(f"Map generated: rooms={rooms_count}")

                # Log more details about map_layout
                if map_layout.rooms:
                    logger.info(
                        f"Room details: first room bounds={map_layout.rooms[0].get_bound() if rooms_count > 0 else 'N/A'}"
                    )
                logger.info(
                    f"Hallways count: {len(map_layout.hallways) if map_layout.hallways else 0}"
                )
                logger.info(
                    f"Doors count: {len(map_layout.doors) if map_layout.doors else 0}"
                )

                if map_manager is None:
                    logger.error("Failed to generate map manager")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                if map_manager._content is None:
                    logger.error("map_manager._content is None")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                logger.info(f"Map content size: {len(map_manager._content)}")

                if not map_layout.rooms or len(map_layout.rooms) < 2:
                    logger.error(f"Insufficient rooms generated: {rooms_count}")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                map_manager.save_snapshot(
                    "level_initial.txt",
                    f"Initial level generation. Difficulty: {difficulty}, Scale: {map_scale}",
                )

                map_manager.ray_caster = RaycastingVisibility(map_manager)

                entity_placer = EntityPlacer(map_manager=map_manager)
                behavior_enforcer = BehaviorEnforcer(
                    map_manager=map_manager, player=player
                )
                enemy_manager = EnemyManager(map_manager, behavior_enforcer)

                rooms_order = list(range(len(map_layout.rooms)))
                random.shuffle(rooms_order)

                # Ensure we have at least 2 rooms for enter and exit
                if len(rooms_order) < 2:
                    logger.error(f"Not enough rooms for enter/exit: {len(rooms_order)}")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                enter_room = rooms_order.pop()
                exit_room = rooms_order.pop()
                start_pos = map_layout.rooms[enter_room].random_point_inside_padded
                exit_pos = map_layout.rooms[exit_room].random_point_inside_padded

                # Validate that positions are within map bounds
                bounds = map_manager.get_bounds()
                if not (
                    bounds[0] <= start_pos.y <= bounds[2]
                    and bounds[1] <= start_pos.x <= bounds[3]
                ):
                    logger.error(f"Start position {start_pos} out of bounds {bounds}")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None
                if not (
                    bounds[0] <= exit_pos.y <= bounds[2]
                    and bounds[1] <= exit_pos.x <= bounds[3]
                ):
                    logger.error(f"Exit position {exit_pos} out of bounds {bounds}")
                    if attempt < retries - 1:
                        logger.info("Retrying with new seed...")
                        seed = int(time.time())
                        continue
                    return None

                level = Level(
                    map_layout=map_layout,
                    map_manager=map_manager,
                    enemy_manager=enemy_manager,
                    entity_placer=entity_placer,
                    exit_point=exit_pos,
                )

                actual_start_pos = (
                    player_start_point if player_start_point is not None else start_pos
                )
                level.entity_placer.place(player, actual_start_pos)
                exit_entity = Entity()
                exit_entity.name = STRINGS.EXIT
                exit_entity.cell = ExitCell()
                exit_entity.cell.owner = exit_entity
                exit_entity.art = (
                    "  ╔═══╗  ",
                    "  ║ E ║  ",
                    "  ║ E ║  ",
                    "  ║ E ║  ",
                    "  ╚═══╝  ",
                )
                level.entity_placer.place(exit_entity, exit_pos)

                content_generator = ContentGenerator(
                    level=level, props=prop, difficulty=difficulty
                )
                content_generator.difficulty_profile = diff_profile

                num_pairs = min(3, max(1, difficulty // 5))

                content_generator.generate_locked_doors_and_keys(
                    start_pos, exit_pos, num_pairs
                )

                content_generator.generate_content(rooms_order)

                if opened_doors:
                    for door_id in opened_doors:
                        points_to_remove = []
                        for point, cell in map_manager._content.items():
                            if (
                                isinstance(cell, LockedDoorCell)
                                and cell.door_id == door_id
                            ):
                                points_to_remove.append(point)
                        for point in points_to_remove:
                            del map_manager[point]
                        logger.info(f"Removed opened door: {door_id}")

                    keys_to_remove = []
                    for point, cell in map_manager._content.items():
                        owner = getattr(cell, "owner", None)
                        if owner is not None:
                            if (
                                hasattr(owner, "opens_door_id")
                                and owner.opens_door_id in opened_doors
                            ):
                                keys_to_remove.append(point)
                    for point in keys_to_remove:
                        del map_manager[point]
                        logger.info(
                            f"Removed used key for door {opened_doors} at {point}"
                        )

                return level

            except Exception as e:
                logger.exception(
                    f"Error generating level (attempt {attempt + 1}/{retries}): {e}"
                )
                if attempt < retries - 1:
                    logger.info("Retrying with new seed...")
                    seed = int(time.time())
                    continue
                else:
                    import traceback

                    traceback.print_exc()
                    return None
        return None
