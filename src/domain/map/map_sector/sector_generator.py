"""Модуль для генерации секторов карты.

Содержит класс SectorGenerator, который создает сетку секторов для последующего
размещения комнат.
"""

from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.point import Point
from domain.map.map_sector.sector import Sector


class SectorGenerator:
    """Генератор секторов карты."""

    @staticmethod
    def gen_sec(
        map_generator_property: MapGenProp,
    ) -> tuple[Sector, ...]:
        """Генерирует сетку секторов 3x3.

        Args:
            map_generator_property: Свойства генерации карты

        Returns:
            Кортеж из 9 секторов, расположенных сеткой 3x3

        """
        dg = map_generator_property
        sectors_height = (dg.sector_height, dg.sector_height, dg.sector_height)
        sectors_width = (dg.sector_width, dg.sector_width, dg.sector_width)
        start_y, start_x = 0, 0
        sectors = []
        for row in range(3):
            for col in range(3):
                sector = Sector(
                    map_generator_property,
                    Point(start_y, start_x),
                    int(dg.sector_pedding),
                    sectors_height[row],
                    sectors_width[col],
                )
                sectors.append(sector)
                start_x += sectors_width[col] + 1
            start_y += sectors_height[row] + 1
            start_x = 0
        return tuple(sectors)
