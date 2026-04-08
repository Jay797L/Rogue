from domain.base.utils.point import Point


class Hallway:
    """Коридор, соединяющий комнаты."""

    def __init__(self, points: set[Point] | None = None):
        """Инициализирует коридор.

        Args:
            points: Множество точек коридора

        """
        self.points = points if points is not None else set()

    def __repr__(self) -> str:
        """Возвращает строковое представление."""
        return f"Hallway(points={len(self.points)})"

    def add_point(self, point: Point) -> None:
        """Добавляет точку в коридор.

        Args:
            point: Точка для добавления

        """
        self.points.add(point)

    def add_points(self, points: set[Point]) -> None:
        """Добавляет множество точек в коридор.

        Args:
            points: Множество точек для добавления

        """
        self.points.update(points)

    @property
    def start_point(self) -> Point | None:
        """Возвращает начальную точку коридора."""
        if not self.points:
            return None
        return min(self.points, key=lambda p: (p.y, p.x))

    @property
    def end_point(self) -> Point | None:
        """Возвращает конечную точку коридора."""
        if not self.points:
            return None
        return max(self.points, key=lambda p: (p.y, p.x))
