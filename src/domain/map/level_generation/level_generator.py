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
    ) -> Level | None:
        """Генерирует уровень с динамической сложностью."""
        try:
            if seed is None:
                seed = int(time.time())

            player_power = difficulty_calculator.calculate_player_power(player)
            diff_profile = difficulty_calculator.calculate_difficulty(
                difficulty, player_power
            )
            map_scale = difficulty_calculator.get_map_scale(difficulty)

            logger.info(
                f"Generating level: difficulty={difficulty}, seed={seed}, map_scale={map_scale}"
            )
            logger.info(f"Player power={player_power}, diff_profile={diff_profile}")

            prop = MapGenProp(
                seed=seed,
                map_scale=map_scale,
                enemies_at_level=max(1, int(3 * diff_profile.enemy_count_multiplier)),
                items_at_level=max(1, int(2 * diff_profile.item_quality_multiplier)),
            )

            logger.info(
                f"MapGenProp created: min_room_height={prop.min_room_height}, min_room_width={prop.min_room_width}"
            )

            map_layout, map_manager = MapGenerator.generate_map(prop)
            logger.info(
                f"Map generated: rooms={len(map_layout.rooms) if map_layout else 0}"
            )

            if map_manager is None:
                logger.error("Failed to generate map manager")
                return None

            map_manager.save_snapshot(
                "level_initial.txt",
                f"Initial level generation. Difficulty: {difficulty}, Scale: {map_scale}",
            )

            map_manager.ray_caster = RaycastingVisibility(map_manager)

            entity_placer = EntityPlacer(map_manager=map_manager)
            behavior_enforcer = BehaviorEnforcer(map_manager=map_manager, player=player)
            enemy_manager = EnemyManager(map_manager, behavior_enforcer)

            if not map_layout.rooms:
                logger.error("No rooms generated")
                return None

            rooms_order = list(range(len(map_layout.rooms)))
            random.shuffle(rooms_order)
            enter_room = rooms_order.pop()
            exit_room = rooms_order.pop()
            start_pos = map_layout.rooms[enter_room].random_point_inside_padded
            exit_pos = map_layout.rooms[exit_room].random_point_inside_padded

            level = Level(
                map_layout=map_layout,
                map_manager=map_manager,
                enemy_manager=enemy_manager,
                entity_placer=entity_placer,
                exit_point=exit_pos,
            )

            level.entity_placer.place(player, start_pos)
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
                    for point, cell in map_manager._content.items():
                        if isinstance(cell, LockedDoorCell) and cell.door_id == door_id:
                            del map_manager[point]

            return level

        except Exception as e:
            logger.exception(f"Error generating level: {e}")
            import traceback

            traceback.print_exc()
            return None
