"""Модуль для генерации полной карты в формате словаря {Point: Cell}.

Объединяет все компоненты генерации: комнаты, коридоры, двери и создает
итоговую карту с клетками.
"""

import random

from domain.base.data.cell_presets import DoorCell, HallwayCell, WallCell
from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.directions import ALL_DIRECTIONS
from domain.map.dead_end_generation.dead_end_generator import DeadEndGenerator
from domain.map.hallway_generation.hallways_generator import HallwaysGenerator
from domain.map.map_assembly.map_layout import MapLayout
from domain.map.map_assembly.map_manager import MapManager
from domain.map.map_cleaner import MapCleaner
from domain.map.map_graph.graph_generator import GraphGenerator
from domain.map.map_room.room_generator import RoomGenerator


class MapGenerator:
    """Генератор карты, создающий словарь {Point: Cell}."""

    @staticmethod
    def generate_map(
        map_property: MapGenProp,
    ) -> tuple[MapLayout, MapManager]:
        """Генерирует полную карту с клетками."""

        map_layout = MapGenerator._generate_map_layout(map_property)
        map_manager = MapManager()
        MapGenerator._add_rooms(map_manager, map_layout)
        MapGenerator._add_hallways(map_manager, map_layout)
        MapGenerator._add_doors(map_manager, map_layout)
        MapGenerator._open_doors(map_manager, map_layout)
        map_manager = MapCleaner.clean_map(map_layout, map_manager)

        return map_layout, map_manager

    @staticmethod
    def _generate_map_layout(map_property: MapGenProp) -> MapLayout:
        """Генерирует макет карты (только структура, без клеток)."""
        map_data = MapLayout(map_property)
        random.seed(map_data.map_property.seed)
        map_data.graph = GraphGenerator.gen_random_graph()
        map_data.rooms = RoomGenerator.gen_all_rooms(map_data.map_property)
        map_data.doors, map_data.hallways = (
            HallwaysGenerator.gen_all_hallways_and_doors(map_data, map_data.graph)
        )
        doors, deadends = DeadEndGenerator.generate_dead_ends(map_data)
        map_data.doors.extend(doors)
        map_data.hallways.extend(deadends)
        return map_data

    @staticmethod
    def _add_rooms(map_manager: MapManager, map_layout: MapLayout) -> None:
        """Добавляет комнаты на карту."""
        for room in map_layout.rooms:
            for direction in ALL_DIRECTIONS:
                wall = room.select_wall(direction)
                for point in wall:
                    if point not in map_manager:
                        map_manager[point] = WallCell()

    @staticmethod
    def _add_hallways(map_manager: MapManager, map_layout: MapLayout) -> None:
        """Добавляет коридоры на карту."""
        for hallway in map_layout.hallways:
            for point in hallway.points:
                if point not in map_manager:
                    map_manager[point] = HallwayCell()

    @staticmethod
    def _add_doors(map_manager: MapManager, map_layout: MapLayout) -> None:
        """Добавляет двери на карту."""
        for door_point in map_layout.doors:
            map_manager[door_point] = DoorCell()

    @staticmethod
    def _open_doors(map_manager: MapManager, map_layout: MapLayout) -> None:
        """Удаляет двери с карты."""
        for door_point in map_layout.doors:
            if door_point in map_manager:
                del map_manager[door_point]
