from domain.base.utils.lines import (
    _generate_points,
    bresenham,
    generate_line_between_points,
    generate_line_points,
    generate_path_line,
    path_algorithm,
    path_between_points,
)
from domain.base.utils.point import Point


class TestBresenham:
    """Tests for the Bresenham line algorithm."""

    @staticmethod
    def test_horizontal_line():
        y1, x1, y2, x2 = (0, 0, 5, 0)
        expected = [Point(y, 0) for y in range(6)]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_vertical_line():
        y1, x1, y2, x2 = (0, 0, 0, 5)
        expected = [Point(0, x) for x in range(6)]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_diagonal_line():
        y1, x1, y2, x2 = (0, 0, 5, 5)
        expected = [Point(i, i) for i in range(6)]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_line_slope_less_than_one():
        y1, x1, y2, x2 = (0, 0, 2, 5)
        expected = [
            Point(0, 0),
            Point(0, 1),
            Point(1, 2),
            Point(1, 3),
            Point(2, 4),
            Point(2, 5),
        ]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_line_slope_greater_than_one():
        y1, x1, y2, x2 = (0, 0, 5, 2)
        expected = [
            Point(0, 0),
            Point(1, 0),
            Point(2, 1),
            Point(3, 1),
            Point(4, 2),
            Point(5, 2),
        ]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_negative_slope():
        y1, x1, y2, x2 = (5, 0, 0, 5)
        expected = [
            Point(5, 0),
            Point(4, 1),
            Point(3, 2),
            Point(2, 3),
            Point(1, 4),
            Point(0, 5),
        ]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_reverse_order():
        y1, x1, y2, x2 = (0, 5, 5, 0)
        expected = [
            Point(0, 5),
            Point(1, 4),
            Point(2, 3),
            Point(3, 2),
            Point(4, 1),
            Point(5, 0),
        ]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_single_point():
        y1, x1, y2, x2 = (3, 3, 3, 3)
        expected = [Point(3, 3)]
        result = bresenham(y1, x1, y2, x2)
        assert result == expected


class TestPathAlgorithm:
    """Tests for the 4‑connected path algorithm."""

    @staticmethod
    def test_horizontal_line():
        y1, x1, y2, x2 = (0, 0, 5, 0)
        expected = [Point(y, 0) for y in range(6)]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_vertical_line():
        y1, x1, y2, x2 = (0, 0, 5, 0)
        expected = [Point(y, 0) for y in range(6)]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_diagonal_line():
        y1, x1, y2, x2 = (0, 0, 5, 5)
        expected = [
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 2),
            Point(2, 2),
            Point(2, 3),
            Point(3, 3),
            Point(3, 4),
            Point(4, 4),
            Point(4, 5),
            Point(5, 5),
        ]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_slope_less_than_one():
        y1, x1, y2, x2 = (0, 0, 5, 2)
        expected = [
            Point(0, 0),
            Point(1, 0),
            Point(1, 1),
            Point(2, 1),
            Point(3, 1),
            Point(3, 2),
            Point(4, 2),
            Point(5, 2),
        ]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_slope_greater_than_one():
        y1, x1, y2, x2 = (0, 0, 2, 5)
        expected = [
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 2),
            Point(1, 3),
            Point(2, 3),
            Point(2, 4),
            Point(2, 5),
        ]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_negative_slope():
        y1, x1, y2, x2 = (5, 0, 0, 5)
        expected = [
            Point(5, 0),
            Point(5, 1),
            Point(4, 1),
            Point(4, 2),
            Point(3, 2),
            Point(3, 3),
            Point(2, 3),
            Point(2, 4),
            Point(1, 4),
            Point(1, 5),
            Point(0, 5),
        ]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_reverse_order():
        y1, x1, y2, x2 = (5, 0, 0, 5)
        expected = [
            Point(5, 0),
            Point(5, 1),
            Point(4, 1),
            Point(4, 2),
            Point(3, 2),
            Point(3, 3),
            Point(2, 3),
            Point(2, 4),
            Point(1, 4),
            Point(1, 5),
            Point(0, 5),
        ]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected

    @staticmethod
    def test_single_point():
        y1, x1, y2, x2 = (3, 3, 3, 3)
        expected = [Point(3, 3)]
        result = path_algorithm(y1, x1, y2, x2)
        assert result == expected


class TestGeneratePoints:
    """Tests for the internal _generate_points function."""

    @staticmethod
    def test_vertical_line():
        start = Point(0, 0)
        end = Point(5, 0)
        expected = [Point(y, 0) for y in range(6)]
        result = _generate_points(start, end, bresenham)
        assert result == expected

    @staticmethod
    def test_horizontal_line():
        start = Point(0, 0)
        end = Point(0, 5)
        expected = [Point(0, x) for x in range(6)]
        result = _generate_points(start, end, bresenham)
        assert result == expected

    @staticmethod
    def test_diagonal_line():
        start = Point(0, 0)
        end = Point(5, 5)
        expected = bresenham(0, 0, 5, 5)
        result = _generate_points(start, end, bresenham)
        assert result == expected

    @staticmethod
    def test_same_point():
        start = end = Point(3, 3)
        expected = [start]
        result = _generate_points(start, end, bresenham)
        assert result == expected

    @staticmethod
    def test_with_path_algorithm():
        start = Point(0, 0)
        end = Point(5, 5)
        expected = path_algorithm(0, 0, 5, 5)
        result = _generate_points(start, end, path_algorithm)
        assert result == expected


class TestGenerateLinePoints:
    """Tests for generate_line_points (Bresenham wrapper)."""

    @staticmethod
    def test_basic_line():
        start = Point(0, 0)
        end = Point(5, 5)
        expected = bresenham(0, 0, 5, 5)
        result = generate_line_points(start, end)
        assert result == expected

    @staticmethod
    def test_same_point():
        start = end = Point(2, 2)
        expected = [start]
        result = generate_line_points(start, end)
        assert result == expected


class TestGeneratePathLine:
    """Tests for generate_path_line (4‑connected wrapper)."""

    @staticmethod
    def test_basic_line():
        start = Point(0, 0)
        end = Point(5, 5)
        expected = path_algorithm(0, 0, 5, 5)
        result = generate_path_line(start, end)
        assert result == expected

    @staticmethod
    def test_same_point():
        start = end = Point(2, 2)
        expected = [start]
        result = generate_path_line(start, end)
        assert result == expected


class TestGenerateLineBetweenPoints:
    """Tests for generate_line_between_points (excludes endpoints)."""

    @staticmethod
    def test_horizontal_line():
        start = Point(0, 0)
        end = Point(0, 5)
        expected = [Point(0, x) for x in range(1, 5)]
        result = generate_line_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_vertical_line():
        start = Point(0, 0)
        end = Point(5, 0)
        expected = [Point(y, 0) for y in range(1, 5)]
        result = generate_line_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_diagonal_line():
        start = Point(0, 0)
        end = Point(5, 5)
        full = bresenham(0, 0, 5, 5)
        expected = full[1:-1]
        result = generate_line_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_same_point():
        start = end = Point(2, 2)
        result = generate_line_between_points(start, end)
        assert result == []


class TestPathBetweenPoints:
    """Tests for path_between_points (4‑connected, excludes endpoints)."""

    @staticmethod
    def test_horizontal_line():
        start = Point(0, 0)
        end = Point(0, 5)
        expected = [Point(0, x) for x in range(1, 5)]
        result = path_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_vertical_line():
        start = Point(0, 0)
        end = Point(5, 0)
        expected = [Point(y, 0) for y in range(1, 5)]
        result = path_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_diagonal_line():
        start = Point(0, 0)
        end = Point(5, 5)
        full = path_algorithm(0, 0, 5, 5)
        expected = full[1:-1]
        result = path_between_points(start, end)
        assert result == expected

    @staticmethod
    def test_same_point():
        start = end = Point(2, 2)
        result = path_between_points(start, end)
        assert result == []
