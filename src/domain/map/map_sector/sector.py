from domain.base.data.map_gen_prop import MapGenProp
from domain.base.utils.directions import DOWN, RIGHT, UP
from domain.base.utils.lines import generate_line_points
from domain.base.utils.point import Point


class Sector:
    """Сектор карты, содержащий комнату."""

    def __init__(
        self,
        map_gen_property: MapGenProp,
        start_position: Point,
        pedding: int,
        height: int,
        width: int,
    ):
        """Инициализирует сектор.

        Args:
            map_gen_property: Свойства генерации
            start_position: Начальная позиция сектора
            pedding: Отступ
            height: Высота сектора
            width: Ширина сектора

        """
        self.map_gen_property = map_gen_property
        self.start_position = start_position
        self.pedding = pedding
        self.height = height
        self.width = width

    @property
    def start_room_place_y(self) -> int:
        """Y-координата начала комнаты."""
        return self.start_position.y + self.pedding

    @property
    def start_room_place_x(self) -> int:
        """X-координата начала комнаты."""
        return self.start_position.x + self.pedding

    @property
    def end_room_place_x(self) -> int:
        """X-координата конца комнаты."""
        return self.start_position.x + self.width - self.pedding

    @property
    def end_room_place_y(self) -> int:
        """Y-координата конца комнаты."""
        return self.start_position.y + self.height - self.pedding

    def select_sector_line(self, direction: Point) -> list[Point]:
        if direction == UP:
            return generate_line_points(
                self.start_position, self.start_position + Point(0, self.width)
            )
        if direction == RIGHT:
            return generate_line_points(
                self.start_position + Point(0, self.width),
                self.start_position + Point(self.height, self.width),
            )
        if direction == DOWN:
            return generate_line_points(
                self.start_position + Point(self.height, 0),
                self.start_position + Point(self.height, self.width),
            )
        return generate_line_points(
            self.start_position, self.start_position + Point(self.height, 0)
        )

    def sorted_wall_points(self, direction: Point) -> list[Point]:
        wall_points = self.select_sector_line(direction)
        wall_points = sorted(wall_points, key=lambda p: p.x)
        wall_points = sorted(wall_points, key=lambda p: p.y)
        return wall_points

    def get_corner_points_on_side(self, direction: Point) -> tuple[Point, Point]:
        """
        Возвращает две угловые точки сектора со стороны direction.

        Args:
            direction: Направление (UP, DOWN, LEFT, RIGHT)

        Returns:
            Кортеж из двух угловых точек (левая/верхняя, правая/нижняя)
        """
        wall_points = self.sorted_wall_points(direction)

        if not wall_points:
            raise ValueError(f"No wall points for direction {direction}")

        return wall_points[0], wall_points[-1]

    def get_all_corners(self) -> tuple[Point, Point, Point, Point]:
        """
        Возвращает все четыре угловые точки сектора.

        Returns:
            Кортеж из четырех угловых точек в порядке:
            (верхний_левый, верхний_правый, нижний_правый, нижний_левый)
        """
        y_min = self.start_position.y
        y_max = self.start_position.y + self.height + 1
        x_min = self.start_position.x
        x_max = self.start_position.x + self.width + 1

        top_left = Point(x_min, y_min)
        top_right = Point(x_max, y_min)
        bottom_right = Point(x_max, y_max)
        bottom_left = Point(x_min, y_max)

        return top_left, top_right, bottom_right, bottom_left
