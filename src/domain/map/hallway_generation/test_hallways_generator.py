"""Тесты для генератора коридоров и дверей."""

from unittest.mock import Mock, patch

import pytest

from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.directions import DOWN, LEFT, RIGHT, UP
from domain.base.utils.point import Point
from domain.map.hallway_generation.hallways_generator import HallwaysGenerator
from domain.map.map_room.room import Room
from domain.map.map_sector.sector import Sector


class TestHallwaysGenerator:
    """Тесты для HallwaysGenerator."""

    @pytest.fixture
    def mock_sector(self):
        """Создает мок сектора с заданными границами."""
        sector = Mock(spec=Sector)
        sector.start_position = Point(10, 10)
        sector.end_position = Point(20, 20)
        sector.start_room_place_x = 10
        sector.end_room_place_x = 20
        sector.start_room_place_y = 10
        sector.end_room_place_y = 20
        return sector

    @pytest.fixture
    def mock_room(self, mock_sector):
        """Создает мок комнаты."""
        room = Mock(spec=Room)
        room.sector = mock_sector
        room.get_room_center = Point(15, 15)
        room.sorted_wall_points = Mock(
            return_value=[
                Point(10, 12),
                Point(10, 13),
                Point(10, 14),
                Point(10, 15),
                Point(10, 16),
                Point(10, 17),
            ]
        )
        return room

    @pytest.fixture
    def map_property(self):
        """Создает свойства карты."""
        prop = MapGenProp()
        prop.door_pedding = 1
        prop.hallway_depth = 1
        prop.chance_for_expansion = 0.0
        return prop


class TestSixReferencePoints(TestHallwaysGenerator):
    """Тесты для _get_six_reference_points."""

    def test_horizontal_movement_right(self, mock_room):
        """Тест горизонтального движения вправо."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(25, 15)
        dir_start = RIGHT
        hallway_depth = 1

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(10, 12),
                Point(10, 13),
                Point(10, 14),
                Point(10, 15),
                Point(10, 16),
                Point(10, 17),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(25, 12),
                Point(25, 13),
                Point(25, 14),
                Point(25, 15),
                Point(25, 16),
                Point(25, 17),
            ]
        )

        result = HallwaysGenerator._get_six_reference_points(
            start_room, end_room, start, end, dir_start, hallway_depth
        )

        assert len(result) == 6

        assert result[0] == Point(11, 12)
        assert result[1] == Point(11, 17)

        assert result[2].x == start.x
        assert result[3].x == start.x

        assert 10 <= result[2].y <= 20
        assert 10 <= result[3].y <= 20
        assert result[2].y != result[3].y

        assert result[4] == Point(24, 12)
        assert result[5] == Point(24, 17)

    def test_horizontal_movement_left(self, mock_room):
        """Тест горизонтального движения влево."""
        start_room = mock_room
        end_room = mock_room
        start = Point(25, 15)
        end = Point(10, 15)
        dir_start = LEFT
        hallway_depth = 1

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(25, 12),
                Point(25, 13),
                Point(25, 14),
                Point(25, 15),
                Point(25, 16),
                Point(25, 17),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(10, 12),
                Point(10, 13),
                Point(10, 14),
                Point(10, 15),
                Point(10, 16),
                Point(10, 17),
            ]
        )

        result = HallwaysGenerator._get_six_reference_points(
            start_room, end_room, start, end, dir_start, hallway_depth
        )

        assert result[0] == Point(24, 12)
        assert result[1] == Point(24, 17)

        assert result[2].x == start.x
        assert result[3].x == start.x

        assert result[4] == Point(11, 12)
        assert result[5] == Point(11, 17)

    def test_vertical_movement_down(self, mock_room):
        """Тест вертикального движения вниз."""
        start_room = mock_room
        end_room = mock_room
        start = Point(15, 10)
        end = Point(15, 25)
        dir_start = DOWN
        hallway_depth = 1

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 10),
                Point(13, 10),
                Point(14, 10),
                Point(15, 10),
                Point(16, 10),
                Point(17, 10),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 25),
                Point(13, 25),
                Point(14, 25),
                Point(15, 25),
                Point(16, 25),
                Point(17, 25),
            ]
        )

        result = HallwaysGenerator._get_six_reference_points(
            start_room, end_room, start, end, dir_start, hallway_depth
        )

        assert result[0] == Point(12, 11)
        assert result[1] == Point(17, 11)

        assert result[2].y == start.y
        assert result[3].y == start.y

        assert 10 <= result[2].x <= 20
        assert 10 <= result[3].x <= 20
        assert result[2].x != result[3].x

        assert result[4] == Point(12, 24)
        assert result[5] == Point(17, 24)

    def test_vertical_movement_up(self, mock_room):
        """Тест вертикального движения вверх."""
        start_room = mock_room
        end_room = mock_room
        start = Point(15, 25)
        end = Point(15, 10)
        dir_start = UP
        hallway_depth = 1

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 25),
                Point(13, 25),
                Point(14, 25),
                Point(15, 25),
                Point(16, 25),
                Point(17, 25),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 10),
                Point(13, 10),
                Point(14, 10),
                Point(15, 10),
                Point(16, 10),
                Point(17, 10),
            ]
        )

        result = HallwaysGenerator._get_six_reference_points(
            start_room, end_room, start, end, dir_start, hallway_depth
        )

        assert result[0] == Point(12, 24)
        assert result[1] == Point(17, 24)

        assert result[2].y == start.y
        assert result[3].y == start.y

        assert result[4] == Point(12, 11)
        assert result[5] == Point(17, 11)


class TestCorridorReferencePoints(TestHallwaysGenerator):
    """Тесты для corridor_reference_points."""

    def test_valid_points_not_empty(self, mock_room, map_property):
        """Тест: valid_points не должен быть пустым."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        with patch.object(HallwaysGenerator, "_get_six_reference_points") as mock_six:
            mock_six.return_value = (
                Point(11, 12),
                Point(11, 18),
                Point(10, 10),
                Point(10, 20),
                Point(29, 12),
                Point(29, 18),
            )

            result = HallwaysGenerator.corridor_reference_points(
                start_room, end_room, start, end, dir_start, map_property.hallway_depth
            )

            assert len(result) >= 2
            assert start in result or result[0] == start
            assert end in result or result[-1] == end

    def test_horizontal_path_contains_start_and_end(self, mock_room, map_property):
        """Тест: путь содержит начальную и конечную точки."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        result = HallwaysGenerator.corridor_reference_points(
            start_room, end_room, start, end, dir_start, map_property.hallway_depth
        )

        assert result[0] == start or start in result
        assert result[-1] == end or end in result

    def test_vertical_path_contains_start_and_end(self, mock_room, map_property):
        """Тест вертикального пути."""
        start_room = mock_room
        end_room = mock_room
        start = Point(15, 10)
        end = Point(15, 30)
        dir_start = DOWN

        result = HallwaysGenerator.corridor_reference_points(
            start_room, end_room, start, end, dir_start, map_property.hallway_depth
        )

        assert result[0] == start or start in result
        assert result[-1] == end or end in result


class TestBuildHallwayPath(TestHallwaysGenerator):
    """Тесты для build_hallway_path."""

    def test_build_hallway_path_returns_set(self, mock_room, map_property):
        """Тест: возвращается множество точек."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        with patch.object(HallwaysGenerator, "corridor_reference_points") as mock_ref:
            mock_ref.return_value = [Point(10, 15), Point(20, 15), Point(30, 15)]

            with patch(
                "domain.base.utils.shapes.generate_figure_points_path"
            ) as mock_path:
                mock_path.return_value = [Point(10, 15), Point(20, 15), Point(30, 15)]

                with patch("domain.base.utils.shell.generate_shell") as mock_shell:
                    mock_shell.return_value = {
                        Point(10, 15),
                        Point(11, 15),
                        Point(20, 15),
                    }

                    result = HallwaysGenerator.build_hallway_path(
                        start_room, end_room, start, end, dir_start, map_property
                    )

                    assert isinstance(result, set)
                    assert len(result) > 0

    def test_hallway_path_contains_doors(self, mock_room, map_property):
        """Тест: путь содержит точки дверей."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        with patch.object(HallwaysGenerator, "corridor_reference_points") as mock_ref:
            mock_ref.return_value = [start, Point(20, 15), end]

            with patch(
                "domain.base.utils.shapes.generate_figure_points_path"
            ) as mock_path:
                mock_path.return_value = [start, Point(20, 15), end]

                with patch("domain.base.utils.shell.generate_shell") as mock_shell:
                    mock_shell.return_value = {start, Point(11, 15), Point(20, 15), end}

                    result = HallwaysGenerator.build_hallway_path(
                        start_room, end_room, start, end, dir_start, map_property
                    )

                    assert start in result
                    assert end in result


class TestGetConnectionDirections(TestHallwaysGenerator):
    """Тесты для get_connection_directions."""

    def test_horizontal_connection_right(self, mock_room):
        """Тест: соединение по горизонтали вправо."""
        room_a = mock_room
        room_b = mock_room
        room_a.get_room_center = Point(10, 15)
        room_b.get_room_center = Point(20, 15)

        dir_a, dir_b = HallwaysGenerator.get_connection_directions(room_a, room_b)

        assert dir_a == RIGHT
        assert dir_b == LEFT

    def test_horizontal_connection_left(self, mock_room):
        """Тест: соединение по горизонтали влево."""
        room_a = mock_room
        room_b = mock_room
        room_a.get_room_center = Point(20, 15)
        room_b.get_room_center = Point(10, 15)

        dir_a, dir_b = HallwaysGenerator.get_connection_directions(room_a, room_b)

        assert dir_a == LEFT
        assert dir_b == RIGHT

    def test_vertical_connection_down(self, mock_room):
        """Тест: соединение по вертикали вниз."""
        room_a = mock_room
        room_b = mock_room
        room_a.get_room_center = Point(15, 10)
        room_b.get_room_center = Point(15, 20)

        dir_a, dir_b = HallwaysGenerator.get_connection_directions(room_a, room_b)

        assert dir_a == DOWN
        assert dir_b == UP

    def test_vertical_connection_up(self, mock_room):
        """Тест: соединение по вертикали вверх."""
        room_a = mock_room
        room_b = mock_room
        room_a.get_room_center = Point(15, 20)
        room_b.get_room_center = Point(15, 10)

        dir_a, dir_b = HallwaysGenerator.get_connection_directions(room_a, room_b)

        assert dir_a == UP
        assert dir_b == DOWN


class TestSelectDoorPoint(TestHallwaysGenerator):
    """Тесты для select_door_point."""

    def test_select_door_point_with_enough_space(self, mock_room):
        """Тест: выбор точки двери при достаточном пространстве."""
        room = mock_room
        direction = RIGHT
        door_pedding = 1

        wall_points = [Point(10, 12), Point(10, 13), Point(10, 14), Point(10, 15)]
        room.sorted_wall_points = Mock(return_value=wall_points)

        result = HallwaysGenerator.select_door_point(room, direction, door_pedding)

        assert result in wall_points[door_pedding:-door_pedding]

    def test_select_door_point_insufficient_space(self, mock_room):
        """Тест: выбор точки двери при недостаточном пространстве."""
        room = mock_room
        direction = RIGHT
        door_pedding = 3

        wall_points = [Point(10, 12), Point(10, 13), Point(10, 14)]
        room.sorted_wall_points = Mock(return_value=wall_points)

        result = HallwaysGenerator.select_door_point(room, direction, door_pedding)

        assert result == wall_points[len(wall_points) // 2]


class TestCorridorDoorsPoints(TestHallwaysGenerator):
    """Тесты для corridor_doors_points."""

    def test_corridor_doors_points_horizontal(self):
        """Тест: точки дверей для горизонтального коридора."""
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        result = HallwaysGenerator.corridor_doors_points(start, end, dir_start)

        expected = {
            Point(10, 15),
            Point(10, 16),
            Point(10, 14),
            Point(30, 15),
            Point(30, 16),
            Point(30, 14),
        }
        assert result == expected

    def test_corridor_doors_points_vertical(self):
        """Тест: точки дверей для вертикального коридора."""
        start = Point(15, 10)
        end = Point(15, 30)
        dir_start = DOWN

        result = HallwaysGenerator.corridor_doors_points(start, end, dir_start)

        expected = {
            Point(15, 10),
            Point(16, 10),
            Point(14, 10),
            Point(15, 30),
            Point(16, 30),
            Point(14, 30),
        }
        assert result == expected


class TestCleaning(TestHallwaysGenerator):
    """Тесты для cleaning."""

    def test_cleaning_horizontal(self):
        """Тест: очистка точек для горизонтального движения."""
        points = {
            Point(5, 10),
            Point(10, 10),
            Point(15, 10),
            Point(20, 10),
            Point(25, 10),
            Point(5, 15),
        }
        doors = {Point(10, 10), Point(20, 10)}
        direction = RIGHT

        result = HallwaysGenerator.cleaning(points, doors, direction)

        expected = {Point(10, 10), Point(15, 10), Point(20, 10)}
        assert result == expected

    def test_cleaning_vertical(self):
        """Тест: очистка точек для вертикального движения."""
        points = {
            Point(10, 5),
            Point(10, 10),
            Point(10, 15),
            Point(10, 20),
            Point(10, 25),
            Point(15, 10),
        }
        doors = {Point(10, 10), Point(10, 20)}
        direction = DOWN

        result = HallwaysGenerator.cleaning(points, doors, direction)

        expected = {Point(10, 10), Point(10, 15), Point(10, 20)}
        assert result == expected

    def test_cleaning_no_doors(self):
        """Тест: очистка при отсутствии дверей."""
        points = {Point(10, 10), Point(15, 10), Point(20, 10)}
        doors = set()
        direction = RIGHT

        result = HallwaysGenerator.cleaning(points, doors, direction)

        assert result == points


class TestBuildStraightPath(TestHallwaysGenerator):
    """Тесты для _build_straight_path."""

    def test_straight_path_horizontal(self):
        """Тест: прямой горизонтальный путь."""
        start = Point(10, 15)
        end = Point(30, 15)
        moving_horizontally = True

        result = HallwaysGenerator._build_straight_path(start, end, moving_horizontally)

        mid_x = (10 + 30) // 2
        expected = [start, Point(mid_x, start.y), Point(mid_x, end.y), end]
        assert result == expected

    def test_straight_path_vertical(self):
        """Тест: прямой вертикальный путь."""
        start = Point(15, 10)
        end = Point(15, 30)
        moving_horizontally = False

        result = HallwaysGenerator._build_straight_path(start, end, moving_horizontally)

        mid_y = (10 + 30) // 2
        expected = [start, Point(start.x, mid_y), Point(end.x, mid_y), end]
        assert result == expected


class TestIntegration(TestHallwaysGenerator):
    """Интеграционные тесты."""

    def test_full_hallway_generation_horizontal(self, mock_room, map_property):
        """Тест: полная генерация горизонтального коридора."""
        start_room = mock_room
        end_room = mock_room
        start = Point(10, 15)
        end = Point(30, 15)
        dir_start = RIGHT

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(10, 12),
                Point(10, 13),
                Point(10, 14),
                Point(10, 15),
                Point(10, 16),
                Point(10, 17),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(30, 12),
                Point(30, 13),
                Point(30, 14),
                Point(30, 15),
                Point(30, 16),
                Point(30, 17),
            ]
        )

        result = HallwaysGenerator.build_hallway_path(
            start_room, end_room, start, end, dir_start, map_property
        )

        assert isinstance(result, set)
        assert start in result
        assert end in result

    def test_full_hallway_generation_vertical(self, mock_room, map_property):
        """Тест: полная генерация вертикального коридора."""
        start_room = mock_room
        end_room = mock_room
        start = Point(15, 10)
        end = Point(15, 30)
        dir_start = DOWN

        start_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 10),
                Point(13, 10),
                Point(14, 10),
                Point(15, 10),
                Point(16, 10),
                Point(17, 10),
            ]
        )
        end_room.sorted_wall_points = Mock(
            return_value=[
                Point(12, 30),
                Point(13, 30),
                Point(14, 30),
                Point(15, 30),
                Point(16, 30),
                Point(17, 30),
            ]
        )

        result = HallwaysGenerator.build_hallway_path(
            start_room, end_room, start, end, dir_start, map_property
        )

        assert isinstance(result, set)
        assert start in result
        assert end in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
