"""Модуль для генерации комнат в секторах карты.

Содержит класс RoomGenerator, который создает комнаты внутри предварительно
сгенерированных секторов.
"""

import random

from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.point import Point
from domain.map.map_room.room import Room
from domain.map.map_sector.sector import Sector
from domain.map.map_sector.sector_generator import SectorGenerator


class RoomGenerator:
    """Генератор комнат внутри секторов карты."""

    @staticmethod
    def gen_all_rooms(map_property: MapGenProp) -> list[Room]:
        """Генерирует все комнаты для карты.

        Args:
            map_property: Свойства генерации карты

        Returns:
            Список сгенерированных комнат

        """
        sectors = SectorGenerator.gen_sec(map_property)
        rooms = []
        for sector in sectors:
            new_room = RoomGenerator.gen_room(sector)
            rooms.append(new_room)
        return rooms

    @staticmethod
    def random_y(sector: Sector) -> int:
        """Генерирует случайную Y-координату для комнаты в секторе.

        Args:
            sector: Сектор, в котором генерируется комната

        Returns:
            Случайная Y-координата

        """
        y = random.randint(
            sector.start_room_place_y,
            sector.end_room_place_y - sector.map_gen_property.min_room_height,
        )
        return y

    @staticmethod
    def random_x(sector: Sector) -> int:
        """Генерирует случайную X-координату для комнаты в секторе.

        Args:
            sector: Сектор, в котором генерируется комната

        Returns:
            Случайная X-координата

        """
        x = random.randint(
            sector.start_room_place_x,
            sector.end_room_place_x - sector.map_gen_property.min_room_width,
        )
        return x

    @staticmethod
    def rand_room_position(sector: Sector) -> Point:
        """Генерирует случайную позицию для комнаты в секторе.

        Args:
            sector: Сектор, в котором генерируется комната

        Returns:
            Точка с координатами комнаты

        """
        y_coord = RoomGenerator.random_y(sector)
        x_coord = RoomGenerator.random_x(sector)
        return Point(y_coord, x_coord)

    @staticmethod
    def max_room_height(sector: Sector, room_position: Point) -> int:
        """Вычисляет максимально возможную высоту комнаты в заданной позиции.

        Args:
            sector: Сектор, содержащий комнату
            room_position: Позиция комнаты

        Returns:
            Максимальная высота комнаты

        """
        max_height_room = sector.end_room_place_y - room_position.y
        return max_height_room

    @staticmethod
    def max_room_width(sector: Sector, room_position: Point) -> int:
        """Вычисляет максимально возможную ширину комнаты в заданной позиции.

        Args:
            sector: Сектор, содержащий комнату
            room_position: Позиция комнаты

        Returns:
            Максимальная ширина комнаты

        """
        max_width_room = sector.end_room_place_x - room_position.x
        return max_width_room

    @staticmethod
    def min_room_height(sector: Sector) -> int:
        """Возвращает минимальную высоту комнаты из свойств генерации.

        Args:
            sector: Сектор, содержащий комнату

        Returns:
            Минимальная высота комнаты

        """
        min_height_room = sector.map_gen_property.min_room_height
        return min_height_room

    @staticmethod
    def min_room_width(sector: Sector) -> int:
        """Возвращает минимальную ширину комнаты из свойств генерации.

        Args:
            sector: Сектор, содержащий комнату

        Returns:
            Минимальная ширина комнаты

        """
        min_width_room = sector.map_gen_property.min_room_width
        return min_width_room

    @staticmethod
    def get_scope(sector: Sector) -> tuple[Point, int, int, int, int]:
        """Получает все параметры для генерации комнаты в секторе.

        Args:
            sector: Сектор для генерации комнаты

        Returns:
            Кортеж (позиция, макс_высота, макс_ширина, мин_высота, мин_ширина)

        """
        position = RoomGenerator.rand_room_position(sector)
        max_height = RoomGenerator.max_room_height(sector, position)
        max_width = RoomGenerator.max_room_width(sector, position)
        min_height = RoomGenerator.min_room_height(sector)
        min_width = RoomGenerator.min_room_width(sector)
        return position, max_height, max_width, min_height, min_width

    @staticmethod
    def gen_room(sector: Sector) -> Room:
        """Генерирует комнату в заданном секторе.

        Args:
            sector: Сектор для генерации комнаты

        Returns:
            Сгенерированная комната

        """
        position, max_height, max_width, min_height, min_width = (
            RoomGenerator.get_scope(sector)
        )
        height = random.randint(min_height, max_height)
        width = random.randint(min_width, max_width)
        return Room(position, height, width, sector)
