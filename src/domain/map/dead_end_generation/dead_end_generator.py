import random

from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.directions import ALL_DIRECTIONS
from domain.base.utils.point import Point
from domain.map.hallway_generation.hallway import Hallway
from domain.map.hallway_generation.hallways_generator import HallwaysGenerator
from domain.map.map_assembly.map_layout import MapLayout
from domain.map.map_room.room import Room
from domain.map.map_sector.sector import Sector


class DeadEndGenerator:
    """Генератор тупиков (мертвых концов) в лабиринте."""

    @staticmethod
    def generate_dead_ends(map_data: MapLayout) -> list[Hallway]:
        hallways = []
        doors = []
        for room in map_data.rooms:
            for direction in ALL_DIRECTIONS:
                if room.is_wall_free(direction):
                    result = DeadEndGenerator.generate_deadends_and_doors_between_rooms(
                        room, map_data.map_property, direction
                    )
                    door, hallway = result
                    doors.append(door)
                    hallways.append(hallway)
        return doors, hallways

    @staticmethod
    def generate_deadends_and_doors_between_rooms(
        room: Room, map_property: MapGenProp, direction: Point
    ) -> tuple[Point, Hallway]:
        door_a = HallwaysGenerator.select_door_point(
            room,
            direction,
            map_property.door_pedding,
        )
        door_b = DeadEndGenerator.select_door_point_at_sector(
            room.sector, direction, map_property.door_pedding
        )

        hallway_points = HallwaysGenerator.build_hallway_path(
            room,
            room,
            door_a,
            door_b,
            direction,
            map_property,
        )

        [door_a, door_b]
        hallway_points = HallwaysGenerator.cleaning(hallway_points, room, room)

        wall_points = DeadEndGenerator.add_dead_end_wall(
            hallway_points, door_b, direction
        )
        hallway_points.update(wall_points)
        hallway_points.add(door_b)
        hallway = Hallway(hallway_points)
        return door_a, hallway

    @staticmethod
    def select_door_point_at_sector(
        sector: Sector, dir: Point, door_pedding: int
    ) -> Point:
        wall_points = sector.sorted_wall_points(dir)
        if len(wall_points) <= 2 * door_pedding:
            return wall_points[len(wall_points) // 2]

        return random.choice(wall_points[door_pedding:-door_pedding])

    @staticmethod
    def cleaning(
        points: set[Point],
        door: Point,
        direction: Point,
    ) -> set[Point]:
        moving_horizontally = direction.y == 0

        if moving_horizontally:
            if direction.x < 0:
                return {point for point in points if point.x <= door.x}
            else:
                return {point for point in points if point.x >= door.x}

        if direction.y < 0:
            return {point for point in points if point.y <= door.y}
        else:
            return {point for point in points if point.y >= door.y}

    @staticmethod
    def add_dead_end_wall(
        hallway_points: set[Point], door: Point, direction: Point
    ) -> set[Point]:
        """Добавляет стену в конце тупика перпендикулярно направлению.

        Стена проходит через точку door и перпендикулярна направлению движения.
        """
        moving_horizontally = direction.y == 0

        if moving_horizontally:
            x_coord = door.x
            y_coords = [p.y for p in hallway_points if p.x == x_coord]

            if not y_coords:
                return set()

            min_y = min(y_coords)
            max_y = max(y_coords)

            wall_points = {Point(y, x_coord) for y in range(min_y, max_y + 1)}

        else:
            y_coord = door.y
            x_coords = [p.x for p in hallway_points if p.y == y_coord]

            if not x_coords:
                return set()

            min_x = min(x_coords)
            max_x = max(x_coords)

            wall_points = {Point(y_coord, x) for x in range(min_x, max_x + 1)}

        return wall_points
