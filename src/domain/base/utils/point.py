from collections.abc import Iterator
from math import sqrt
from typing import Any, Union

POINT_COORD_COUNT = 2


class Point:
    """Точка на карте с координатами (y, x)."""

    def __init__(self, *args: Any) -> None:
        """Инициализирует точку из двух координат или одного кортежа/списка."""
        if len(args) == POINT_COORD_COUNT:
            y, x = args

            if not isinstance(y, int) or not isinstance(x, int):
                raise TypeError(
                    f"Координаты должны быть целыми числами, получены: y={type(y).__name__}, x={type(x).__name__}"
                )
        elif len(args) == 1:
            arg = args[0]
            if not isinstance(arg, (tuple, list)) or len(arg) != POINT_COORD_COUNT:
                raise TypeError(f"Невозможно создать Point из {arg}")
            y, x = arg
            if not isinstance(y, int) or not isinstance(x, int):
                raise TypeError(
                    f"Координаты должны быть целыми числами, получены: y={type(y).__name__}, x={type(x).__name__}"
                )
        else:
            raise TypeError(f"Некорректное количество аргументов: {len(args)}")
        self.y = y
        self.x = x

    def __iter__(self) -> Iterator[int]:
        """Позволяет распаковывать точку как (y, x)"""
        yield self.y
        yield self.x

    def __add__(self, other: Union["Point", int]) -> "Point":
        """Сложение с Point или целым числом."""
        if isinstance(other, Point):
            return Point(self.y + other.y, self.x + other.x)
        if isinstance(other, int):
            return Point(self.y + other, self.x + other)
        return NotImplemented

    def __sub__(self, other: Union["Point", int]) -> "Point":
        """Вычитание Point или целого числа."""
        if isinstance(other, Point):
            return Point(self.y - other.y, self.x - other.x)
        if isinstance(other, int):
            return Point(self.y - other, self.x - other)
        return NotImplemented

    def __mul__(self, other: Union["Point", int]) -> "Point":
        """Умножение на Point или целое число."""
        if isinstance(other, Point):
            return Point(self.y * other.y, self.x * other.x)
        if isinstance(other, int):
            return Point(self.y * other, self.x * other)
        return NotImplemented

    def __iadd__(self, other: Union["Point", int]) -> "Point":
        """Сложение с присваиванием."""
        if isinstance(other, Point):
            self.y += other.y
            self.x += other.x
        elif isinstance(other, int):
            self.y += other
            self.x += other
        else:
            return NotImplemented
        return self

    def __eq__(self, other: object) -> bool:
        """Сравнение точек."""
        if not isinstance(other, Point):
            return NotImplemented
        return self.y == other.y and self.x == other.x

    def __repr__(self) -> str:
        """Строковое представление точки."""
        return f"(y={self.y}, x={self.x})"

    def distance(self, position: "Point") -> int:
        """Вычисляет манхэттенское расстояние до другой точки.

        Args:
            position: Целевая точка

        Returns:
            Манхэттенское расстояние

        """
        return abs(self.x - position.x) + abs(self.y - position.y)

    def distance_float(self, position: "Point") -> float:
        """Вычисляет евклидово расстояние до другой точки.

        Args:
            position: Целевая точка

        Returns:
            Евклидово расстояние

        """
        dx = abs(self.x - position.x)
        dy = abs(self.y - position.y)
        return float(sqrt(abs(dx * dx + dy * dy)).real)

    def __hash__(self) -> int:
        """Хеш точки."""
        return hash((self.x, self.y))
