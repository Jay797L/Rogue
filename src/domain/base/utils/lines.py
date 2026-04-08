from collections.abc import Callable

from domain.base.utils.point import Point


def bresenham(y1: int, x1: int, y2: int, x2: int) -> list[Point]:
    """Алгоритм Брезенхема для рисования линий."""
    points = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    x, y = x1, y1

    while True:
        points.append(Point(y, x))

        if x == x2 and y == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return points


def path_algorithm(y1: int, x1: int, y2: int, x2: int) -> list[Point]:
    """
    Алгоритм для линий, гарантирующий 4-связность.
    У каждой точки есть сосед по вертикали/горизонтали.
    """
    points = []

    x, y = x1, y1
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    points.append(Point(y, x))

    if dx > dy:
        err = dx / 2.0
        while x != x2:
            err -= dy
            if err < 0:
                y += sy
                points.append(Point(y, x))
                err += dx
            x += sx
            points.append(Point(y, x))
    else:
        err = dy / 2.0
        while y != y2:
            err -= dx
            if err < 0:
                x += sx
                points.append(Point(y, x))
                err += dy
            y += sy
            points.append(Point(y, x))

    return points


def generate_line_points(start: Point, end: Point) -> list[Point]:
    """
    Генерирует линию между двумя точками по алгоритму Брезенхема.

    Args:
        start: Начальная точка
        end: Конечная точка

    Returns:
        Список точек, включая начальную и конечную, в порядке от start к end
    """
    return _generate_points(start, end, bresenham)


def generate_path_line(start: Point, end: Point) -> list[Point]:
    """
    Генерирует линию с 4-связностью между двумя точками.

    Args:
        start: Начальная точка
        end: Конечная точка

    Returns:
        Список точек, включая начальную и конечную, в порядке от start к end
    """
    return _generate_points(start, end, path_algorithm)


def generate_line_between_points(start: Point, end: Point) -> list[Point]:
    """
    Генерирует линию между двумя точками без включения самих точек.

    Args:
        start: Начальная точка (исключается из результата)
        end: Конечная точка (исключается из результата)

    Returns:
        Список точек, образующих линию, без начальной и конечной точек
    """
    points = generate_line_points(start, end)

    if points and points[0] == start:
        points.pop(0)
    if points and points[-1] == end:
        points.pop(-1)
    return points


def _generate_points(
    start_position: Point,
    end_position: Point,
    diagonal_algorithm: Callable,
) -> list[Point]:
    """
    Базовый метод генерации точек между двумя позициями.

    Args:
        start_position: Начальная точка
        end_position: Конечная точка
        diagonal_algorithm: Функция для диагональных линий

    Returns:
        Список точек, образующих линию/путь, в порядке от start к end

    Raises:
        ValueError: Если точки имеют одинаковые координаты
    """
    if start_position == end_position:
        return [start_position]

    x1, y1 = start_position.x, start_position.y
    x2, y2 = end_position.x, end_position.y

    if x1 == x2:
        points = []
        step = 1 if y1 <= y2 else -1
        for y_coord in range(y1, y2 + step, step):
            points.append(Point(y_coord, x1))
        return points

    if y1 != y2:
        return diagonal_algorithm(y1, x1, y2, x2)
    points = []
    step = 1 if x1 <= x2 else -1
    for x_coord in range(x1, x2 + step, step):
        points.append(Point(y1, x_coord))
    return points


def path_between_points(start: Point, end: Point) -> list[Point]:
    """
    Генерирует путь между двумя точками с 4-связностью.
    Исключает начальную и конечную точки.

    Args:
        start: Начальная точка
        end: Конечная точка

    Returns:
        Список точек, образующих путь, без начальной и конечной точек,
        в порядке от start к end
    """
    points = generate_path_line(start, end)

    if points and points[0] == start:
        points.pop(0)
    if points and points[-1] == end:
        points.pop(-1)
    return points
