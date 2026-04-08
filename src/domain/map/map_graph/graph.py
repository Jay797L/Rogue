class GridRenderer:
    """Базовый класс для отрисовки сеток."""

    @staticmethod
    def draw_intersection(grid: list[list[str]], y: int, x: int) -> None:
        """Рисует пересечение в указанной позиции.

        Args:
            grid: Сетка для отрисовки
            y: Y-координата
            x: X-координата

        """
        has_horizontal = (x > 0 and grid[y][x - 1] in ("─", "┼")) or (
            x < len(grid[0]) - 1 and grid[y][x + 1] in ("─", "┼")
        )
        has_vertical = (y > 0 and grid[y - 1][x] in ("│", "┼")) or (
            y < len(grid) - 1 and grid[y + 1][x] in ("│", "┼")
        )

        if has_horizontal and has_vertical:
            grid[y][x] = "┼"
        elif has_horizontal:
            grid[y][x] = "─"
        elif has_vertical:
            grid[y][x] = "│"


class _GraphRenderer(GridRenderer):
    """Внутренний класс для отрисовки графа."""

    NODE_POSITIONS: dict[str, tuple[int, int]] = {
        "0": (0, 0),
        "1": (0, 2),
        "2": (0, 4),
        "3": (2, 0),
        "4": (2, 2),
        "5": (2, 4),
        "6": (4, 0),
        "7": (4, 2),
        "8": (4, 4),
    }

    HORIZONTAL_EDGES: dict[int, tuple[int, int]] = {
        0: (0, 1),
        1: (0, 3),
        5: (2, 1),
        6: (2, 3),
        10: (4, 1),
        11: (4, 3),
    }

    VERTICAL_EDGES: dict[int, tuple[int, int]] = {
        2: (1, 0),
        3: (1, 2),
        4: (1, 4),
        7: (3, 0),
        8: (3, 2),
        9: (3, 4),
    }

    INTERSECTION_POINTS: list[tuple[int, int]] = [
        (1, 1),
        (1, 3),
        (3, 1),
        (3, 3),
    ]

    @classmethod
    def render(cls, graph: "Graph") -> str:
        """Отрисовывает граф в виде строки.

        Args:
            graph: Граф для отрисовки

        Returns:
            Строковое представление графа

        """
        grid = cls._build_grid(graph)
        return cls._format(grid)

    @classmethod
    def _build_grid(cls, graph: "Graph") -> list[list[str]]:
        """Строит сетку для отрисовки графа."""
        grid = [[" " for _ in range(5)] for _ in range(5)]

        for node, (y, x) in cls.NODE_POSITIONS.items():
            grid[y][x] = node

        for bit in range(12):
            if (graph.num >> bit) & 1:
                if bit in cls.HORIZONTAL_EDGES:
                    y, x = cls.HORIZONTAL_EDGES[bit]
                    grid[y][x] = "─"
                elif bit in cls.VERTICAL_EDGES:
                    y, x = cls.VERTICAL_EDGES[bit]
                    grid[y][x] = "│"

        cls._draw_intersections(grid)

        return grid

    @classmethod
    def _draw_intersections(cls, grid: list[list[str]]) -> None:
        """Рисует пересечения на сетке."""
        for y, x in cls.INTERSECTION_POINTS:
            cls.draw_intersection(grid, y, x)

    @staticmethod
    def _format(grid: list[list[str]]) -> str:
        """Форматирует сетку в строку."""
        top = "┌─────────┐"
        middle = "\n".join(f"│{' '.join(row)}│" for row in grid)
        bottom = "└─────────┘"
        return f"{top}\n{middle}\n{bottom}"


class Graph:
    """Граф соединений между комнатами."""

    bit_to_vertices: dict[int, tuple[int, int]] = {
        0: (0, 1),
        1: (1, 2),
        2: (0, 3),
        3: (1, 4),
        4: (2, 5),
        5: (3, 4),
        6: (4, 5),
        7: (3, 6),
        8: (4, 7),
        9: (5, 8),
        10: (6, 7),
        11: (7, 8),
    }

    def __init__(self, num: int):
        """Инициализирует граф.

        Args:
            num: Число-маска соединений

        """
        self.num = num
        self._connections = self._compute_connections()

    def _compute_connections(self) -> tuple[tuple[int, int], ...]:
        """Вычисляет соединения на основе маски."""
        connections = []

        for bit in range(12):
            if (self.num >> bit) & 1:
                a, b = self.bit_to_vertices[bit]
                connections.append((a, b))

        return tuple(connections)

    def __repr__(self) -> str:
        """Возвращает строковое представление графа."""
        return _GraphRenderer.render(self)

    @property
    def connections(self) -> tuple[tuple[int, int], ...]:
        """Возвращает соединения графа."""
        return self._connections
