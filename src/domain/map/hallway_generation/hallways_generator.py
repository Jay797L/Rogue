"""Генератор коридоров и дверей между комнатами."""

import math
import random

from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.directions import DOWN, LEFT, RIGHT, UP
from domain.base.utils.point import Point
from domain.base.utils.shapes import generate_figure_points_path
from domain.base.utils.shell import generate_shell
from domain.map.hallway_generation.hallway import Hallway
from domain.map.map_assembly.map_layout import MapLayout
from domain.map.map_graph.graph import Graph
from domain.map.map_room.room import Room

MAX_DISTANCE_TO_SECTOR_EDGE = 5
DOOR_NEIGHBOR_RADIUS = 2
DEAD_END_DEVIATION = 0
MIN_POINTS_FOR_WINDING = 0
MAX_DEAD_ENDS = 0


MIN_PATH_POINTS = 3
MAX_PATH_POINTS = 3
RANDOM_PATH_CHANCE = 1


class HallwaysGenerator:
    """Генератор коридоров и дверей между комнатами."""

    @staticmethod
    def gen_all_hallways_and_doors(
        map_data: MapLayout,
        graph: Graph,
    ) -> tuple[list[Point], list[Hallway]]:
        """Генерирует все коридоры и двери на основе графа соединений."""
        hallways = []
        connections = graph.connections
        doors = []

        for room_a_idx, room_b_idx in connections:
            result = HallwaysGenerator.generate_hallway_and_doors_between_rooms(
                map_data.rooms[room_a_idx],
                map_data.rooms[room_b_idx],
                map_data.map_property,
            )
            if result:
                door_a, door_b, hallway = result
                doors.append(door_a)
                doors.append(door_b)
                hallways.append(hallway)

        return doors, hallways

    @staticmethod
    def get_directions_connected_rooms(
        room_a: Room,
        room_b: Room,
    ) -> tuple[Point, Point]:
        """Определяет направления соединения между комнатами.

        Args:
            room_a: Первая комната
            room_b: Вторая комната

        Returns:
            Кортеж (направление из комнаты A, направление из комнаты B)

        """
        center_a = room_a.get_room_center
        center_b = room_b.get_room_center
        dy = center_b.y - center_a.y
        dx = center_b.x - center_a.x

        if abs(dy) > abs(dx):
            if dy > 0:
                return DOWN, UP
            return UP, DOWN

        if dx > 0:
            return RIGHT, LEFT
        return LEFT, RIGHT

    @staticmethod
    def generate_hallway_and_doors_between_rooms(
        room_a: Room,
        room_b: Room,
        map_property: MapGenProp,
    ) -> tuple[Point, Point, Hallway]:
        """Генерирует коридор и двери между двумя комнатами.

        Args:
            room_a: Первая комната
            room_b: Вторая комната
            map_property: Свойства генерации карты

        Returns:
            Кортеж (дверь A, дверь B, коридор)
            или
            None если соединение невозможно

        """
        dir_a, dir_b = HallwaysGenerator.get_connection_directions(
            room_a,
            room_b,
        )

        door_a = HallwaysGenerator.select_door_point(
            room_a,
            dir_a,
            map_property.door_pedding,
        )
        door_b = HallwaysGenerator.select_door_point(
            room_b,
            dir_b,
            map_property.door_pedding,
        )
        hallway_points = HallwaysGenerator.build_hallway_path(
            room_a,
            room_b,
            door_a,
            door_b,
            dir_a,
            map_property,
        )
        hallway = Hallway(hallway_points)
        return door_a, door_b, hallway

    @staticmethod
    def select_door_point(
        room: Room,
        direction: Point,
        door_pedding: int,
    ) -> Point:
        """Выбирает точку для двери на стене комнаты.

        Args:
            room: Комната
            direction: Направление стены
            door_pedding: Отступ от краев стены

        Returns:
            Точка для размещения двери

        """
        wall_points = room.sorted_wall_points(direction)
        if len(wall_points) <= 2 * door_pedding:
            return wall_points[len(wall_points) // 2]

        return random.choice(wall_points[door_pedding:-door_pedding])

    @staticmethod
    def get_connection_directions(
        room_a: Room,
        room_b: Room,
    ) -> tuple[Point, Point]:
        """Определяет направления для соединения комнат.

        Args:
            room_a: Первая комната
            room_b: Вторая комната

        Returns:
            Кортеж (направление из A, направление из B)

        """
        center_a = room_a.get_room_center
        center_b = room_b.get_room_center

        dy = center_b.y - center_a.y
        dx = center_b.x - center_a.x

        if abs(dy) > abs(dx):
            if dy > 0:
                return DOWN, UP
            return UP, DOWN

        if dx > 0:
            return RIGHT, LEFT
        return LEFT, RIGHT

    @staticmethod
    def corridor_doors_points(
        start: Point,
        end: Point,
        dir_start: Point,
    ) -> set[Point]:
        """Создает точки для дверей вокруг начала и конца коридора.

        Args:
            start: Начальная точка
            end: Конечная точка
            dir_start: Направление в начале

        Returns:
            Множество точек для дверей

        """
        shift = Point(1, 1) - dir_start
        return {
            start,
            start + shift,
            start - shift,
            end,
            end + shift,
            end - shift,
        }

    @staticmethod
    def cleaning(
        points: set[Point],
        start_room: Room,
        end_room: Room,
    ) -> set[Point]:
        """Очищает точки коридора, удаляя точки, попадающие внутрь комнат.

        Args:
            points: Точки коридора
            start_room: Начальная комната
            end_room: Конечная комната

        Returns:
            Отфильтрованное множество точек

        """
        return {
            point
            for point in points
            if not start_room.in_room(point) and not end_room.in_room(point)
        }

    @staticmethod
    def build_hallway_path(
        start_room: Room,
        end_room: Room,
        start: Point,
        end: Point,
        dir_start: Point,
        map_property: MapGenProp,
    ) -> set[Point]:
        """Строит путь коридора между двумя точками.

        Args:
            start_room: Начальная комната
            end_room: Конечная комната
            start: Начальная точка
            end: Конечная точка
            dir_start: Направление в начале
            map_property: Свойства генерации карты

        Returns:
            Множество точек коридора

        """
        HallwaysGenerator.corridor_doors_points(start, end, dir_start)
        reference_points = HallwaysGenerator.corridor_reference_points(
            start_room,
            end_room,
            start,
            end,
            dir_start,
            map_property.hallway_depth,
        )

        hallway_center_points = generate_figure_points_path(reference_points)

        depth = map_property.hallway_depth
        if random.random() < map_property.chance_for_expansion:
            depth += 1

        hallway_points = generate_shell(points=hallway_center_points, depth=depth)

        hallway_points = HallwaysGenerator.cleaning(
            hallway_points,
            start_room,
            end_room,
        )

        return hallway_points

    @staticmethod
    def _get_sorted_vertices(six_points: tuple[Point, ...]) -> list[Point]:
        """
        Сортирует 6 опорных точек по углу относительно центра масс.
        Возвращает точки в порядке обхода против часовой стрелки.
        """
        points = list(six_points)

        center_x = sum(p.x for p in points) / len(points)
        center_y = sum(p.y for p in points) / len(points)

        points.sort(key=lambda p: math.atan2(p.y - center_y, p.x - center_x))

        return points

    @staticmethod
    def _get_points_in_polygon(vertices: list[Point]) -> set[Point]:
        """
        Возвращает все целочисленные точки, лежащие внутри и на границе
        простого многоугольника (вершины заданы в порядке обхода).
        Используется алгоритм сканирования строк (scanline).
        """
        if len(vertices) < 3:
            return set()

        xs = [p.x for p in vertices]
        ys = [p.y for p in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        points = set()

        def point_in_polygon(px, py):
            inside = False
            n = len(vertices)
            for i in range(n):
                x1, y1 = vertices[i].x, vertices[i].y
                x2, y2 = vertices[(i + 1) % n].x, vertices[(i + 1) % n].y

                if ((y1 > py) != (y2 > py)) and (
                    px < (x2 - x1) * (py - y1) / (y2 - y1) + x1
                ):
                    inside = not inside
            return inside

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if point_in_polygon(y, x):
                    points.add(Point(y, x))
        return points

    @staticmethod
    def _get_six_reference_points(
        start_room: Room,
        end_room: Room,
        start: Point,
        end: Point,
        dir_start: Point,
        hallway_depth: int,
    ) -> tuple[Point, Point, Point, Point, Point, Point]:
        """
        Возвращает 6 опорных точек для построения фигуры:
        - 2 точки стартовой комнаты (ближайшие к сектору + отступ)
        - 2 общие точки между секторами
        - 2 точки конечной комнаты (ближайшие к сектору + отступ)
        """

        dir_end = Point(-dir_start.y, -dir_start.x)
        padding = dir_start * hallway_depth
        start_c1 = start_room.sorted_wall_points(dir_start)[0] + padding
        start_c2 = start_room.sorted_wall_points(dir_start)[-1] + padding

        sector_p1 = start_room.sector.sorted_wall_points(dir_start)[hallway_depth - 1]
        sector_p2 = start_room.sector.sorted_wall_points(dir_start)[-hallway_depth]

        end_c1 = end_room.sorted_wall_points(dir_end)[0] - padding
        end_c2 = end_room.sorted_wall_points(dir_end)[-1] - padding

        return (start_c1, start_c2, sector_p1, sector_p2, end_c1, end_c2)

    @staticmethod
    def corridor_reference_points(
        start_room: Room,
        end_room: Room,
        start: Point,
        end: Point,
        dir_start: Point,
        hallway_depth: int = 1,
    ) -> list[Point]:
        moving_horizontally = dir_start.y == 0

        six_points = HallwaysGenerator._get_six_reference_points(
            start_room, end_room, start, end, dir_start, hallway_depth
        )

        vertices = HallwaysGenerator._get_sorted_vertices(six_points)
        valid_points = HallwaysGenerator._get_points_in_polygon(vertices)

        base_points = HallwaysGenerator._build_random_base_path(
            start, end, moving_horizontally, valid_points
        )

        final_points = HallwaysGenerator._add_dead_ends(
            base_points, valid_points, start, end, moving_horizontally, hallway_depth
        )

        return base_points

    @staticmethod
    def _build_random_base_path(
        start: Point,
        end: Point,
        moving_horizontally: bool,
        valid_points: set[Point],
    ) -> list[Point]:
        """
        Строит базовый путь от start до end, который может быть случайным.
        Использует случайное количество промежуточных точек из валидной области.
        """

        if False:
            return HallwaysGenerator._build_random_path(
                start, end, moving_horizontally, valid_points
            )

        else:
            return HallwaysGenerator._build_straight_path(
                start, end, moving_horizontally
            )

    @staticmethod
    def _build_straight_path(
        start: Point, end: Point, moving_horizontally: bool
    ) -> list[Point]:
        """
        Строит прямой путь (L-образный) от start до end.
        При движении горизонтально (меняется x - строка)
        и вертикально (меняется y - столбец).
        """
        if moving_horizontally:
            mid_x = (start.x + end.x) // 2
            return [start, Point(start.y, mid_x), Point(end.y, mid_x), end]
        else:
            mid_y = (start.y + end.y) // 2
            return [start, Point(mid_y, start.x), Point(mid_y, end.x), end]

    @staticmethod
    def _build_random_path(
        start: Point,
        end: Point,
        moving_horizontally: bool,
        valid_points: set[Point],
    ) -> list[Point]:
        """
        Строит случайный путь с промежуточными точками из valid_points.
        Количество точек выбирается случайно в диапазоне [MIN_PATH_POINTS, MAX_PATH_POINTS].
        """

        num_intermediate = random.randint(MIN_PATH_POINTS, MAX_PATH_POINTS)

        candidate_points = [p for p in valid_points if p not in (start, end)]

        if len(candidate_points) < num_intermediate:
            if len(candidate_points) < MIN_POINTS_FOR_WINDING:
                return HallwaysGenerator._build_straight_path(
                    start, end, moving_horizontally
                )
            intermediate_points = random.sample(candidate_points, len(candidate_points))
        else:
            intermediate_points = random.sample(candidate_points, num_intermediate)

        if moving_horizontally:
            intermediate_points.sort(key=lambda p: p.x)
        else:
            intermediate_points.sort(key=lambda p: p.y)

        path = [start] + intermediate_points + [end]

        return path

    @staticmethod
    def _add_dead_ends(
        base_points: list[Point],
        valid_points: set[Point],
        start: Point,
        end: Point,
        moving_horizontally: bool,
        hallway_depth: int = 1,
    ) -> list[Point]:
        """
        Добавляет тупиковые ответвления в путь, если они есть.
        Возвращает линейную последовательность с возвратами.
        """
        if len(valid_points) < MIN_POINTS_FOR_WINDING:
            return base_points

        dead_end_candidates = HallwaysGenerator._find_dead_end_points(
            valid_points, start, end, moving_horizontally, hallway_depth
        )

        if not dead_end_candidates:
            return base_points

        final_points = []
        current_point = base_points[0]

        for i in range(len(base_points) - 1):
            final_points.append(current_point)

            dead_end = HallwaysGenerator._find_dead_end_between(
                current_point,
                base_points[i + 1],
                dead_end_candidates,
                moving_horizontally,
            )

            if dead_end:
                final_points.append(dead_end)

                final_points.append(current_point)

            current_point = base_points[i + 1]

        final_points.append(end)

        return final_points

    @staticmethod
    def _find_dead_end_points(
        points: set[Point],
        start: Point,
        end: Point,
        moving_horizontally: bool,
        hallway_depth: int = 1,
    ) -> list[Point]:
        """
        Находит точки, которые могут быть тупиками (ответвления от основного пути).
        """
        dead_ends = []

        allowed_deviation = DEAD_END_DEVIATION + hallway_depth

        for point in points:
            if point in (start, end):
                continue

            if moving_horizontally:
                if (
                    abs(point.y - start.y) > allowed_deviation
                    and abs(point.y - end.y) > allowed_deviation
                ):
                    dead_ends.append(point)

            elif (
                abs(point.x - start.x) > allowed_deviation
                and abs(point.x - end.x) > allowed_deviation
            ):
                dead_ends.append(point)

        return dead_ends[:MAX_DEAD_ENDS]

    @staticmethod
    def _find_dead_end_between(
        from_point: Point,
        to_point: Point,
        dead_end_candidates: list[Point],
        moving_horizontally: bool,
    ) -> Point | None:
        """
        Находит тупик, который находится между двумя точками пути.
        """
        if moving_horizontally:
            y_min = min(from_point.y, to_point.y)
            y_max = max(from_point.y, to_point.y)

            for dead_end in dead_end_candidates:
                if y_min <= dead_end.y <= y_max:
                    return dead_end
        else:
            x_min = min(from_point.x, to_point.x)
            x_max = max(from_point.x, to_point.x)

            for dead_end in dead_end_candidates:
                if x_min <= dead_end.x <= x_max:
                    return dead_end

        return None
