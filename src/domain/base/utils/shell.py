from itertools import cycle, islice

from domain.base.utils.directions import ALL_DIRECTIONS
from domain.base.utils.point import Point


def generate_shell(
    points: set[Point] | None = None,
    exclude: set[Point] | None = None,
    depth: int = 1,
) -> set[Point]:
    """Генерирует оболочку вокруг заданных точек.

    Args:
        points: Множество исходных точек
        exclude: Множество точек для исключения
        depth: Глубина оболочки (количество слоев)

        Returns:
            Множество точек оболочки

    """
    if points is None:
        points = set()
    if exclude is None:
        exclude = set()

    current_layer: set[Point] = points.copy()

    all_excluded: set[Point] = exclude.copy()

    for _ in range(depth + 1):
        next_layer: set[Point] = set()
        current_layer.copy()

        all_excluded.update(current_layer)
        directions = [
            a + b
            for a, b in zip(
                ALL_DIRECTIONS, islice(cycle(ALL_DIRECTIONS), 1, None), strict=False
            )
        ] + ALL_DIRECTIONS

        for point in current_layer:
            for direction in directions:
                neighbor = direction + point
                if (
                    neighbor not in current_layer
                    and neighbor not in next_layer
                    and neighbor not in all_excluded
                ):
                    next_layer.add(neighbor)

                    current_layer = next_layer
    return current_layer
