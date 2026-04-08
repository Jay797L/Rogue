from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.point import Point
from domain.map.hallway_generation.hallway import Hallway
from domain.map.map_graph.graph import Graph
from domain.map.map_room.room import Room


class MapLayout:
    """Макет карты со всеми элементами."""

    def __init__(self, map_property: MapGenProp | None = None):
        """Инициализирует макет карты.

        Args:
            map_property: Свойства генерации карты

        """
        self.map_property = map_property or MapGenProp()
        self.hallways: list[Hallway] = []
        self.rooms: list[Room] = []
        self.graph: Graph | None = None
        self.doors: list[Point] = []
