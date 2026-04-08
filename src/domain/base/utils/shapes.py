from domain.base.utils.lines import generate_line_points, generate_path_line
from domain.base.utils.point import Point


def generate_figure_points(points: list[Point]) -> set[Point]:
    """Замкнутая фигура (линии по Брезенхему)."""
    result = set()
    for cur, nxt in zip(points[:-1], points[1:], strict=False):
        result.update(generate_line_points(cur, nxt))
    return result


def generate_figure_points_path(points: list[Point]) -> set[Point]:
    """Замкнутый путь (линии с 4-связностью)."""
    result = set()
    for cur, nxt in zip(points[:-1], points[1:], strict=False):
        result.update(generate_path_line(cur, nxt))
    return result
