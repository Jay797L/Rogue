import logging
from collections import deque

from domain.base.utils.point import Point
from domain.map.map_assembly.map_layout import MapLayout
from domain.map.map_assembly.map_manager import MapManager

logger = logging.getLogger(__name__)


class MapCleaner:
    @staticmethod
    def clean_map(map_layout: MapLayout, old_map_manager: MapManager) -> MapManager:

        old_map_manager.save_snapshot(
            "before_cleaning.txt",
            f"Before cleaning. Total cells: {len(old_map_manager.all_points)}",
        )

        if not map_layout.rooms:
            return old_map_manager
        min_y, min_x, max_y, max_x = old_map_manager.get_bounds()

        def is_point_in_map(point: Point) -> bool:
            return (
                point.y >= min_y
                and point.y <= max_y
                and point.x >= min_x
                and point.x <= max_x
            )

        def is_walkable(point: Point) -> bool:
            return old_map_manager.is_empty(point)

        start_point = map_layout.rooms[0].random_point_inside

        visited_walkable = set()
        boundary_walls = set()
        queue = deque([start_point])
        visited_walkable.add(start_point)

        directions_8 = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        while queue:
            current = queue.popleft()
            for dy, dx in directions_8:
                neighbor = Point(current.y + dy, current.x + dx)

                if neighbor in visited_walkable:
                    continue
                if is_walkable(neighbor):
                    if not is_point_in_map(neighbor):
                        raise RuntimeError("Карта не замкнута")
                    visited_walkable.add(neighbor)
                    queue.append(neighbor)
                else:
                    boundary_walls.add(neighbor)

        new_map_manager = MapManager()

        for point in boundary_walls:
            new_map_manager[point] = old_map_manager[point]

        logger.info(
            "Map cleaned: {} -> {} cells",
            len(old_map_manager.all_points),
            len(new_map_manager.all_points),
        )

        new_map_manager.save_snapshot(
            "after_cleaning.txt",
            f"After cleaning. Removed {len(old_map_manager.all_points) - len(new_map_manager.all_points)} cells",
        )

        return new_map_manager
