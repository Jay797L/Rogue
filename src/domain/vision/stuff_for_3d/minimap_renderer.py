"""Module for rendering minimap in pseudo-3D view."""

from domain.base.core.pixel import Pixel
from domain.base.data.colors import COLORS


class MinimapRenderer:
    """Handles rendering of minimap with rotation."""

    def __init__(self, screen_width: int, screen_height: int, direction: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.direction = direction
        self.minimap_size = 15
        self.minimap_radius = 7
        self.x_offset = 1
        self.y_offset = 1

    def set_direction(self, direction: int) -> None:
        """Update direction for minimap rotation."""
        self.direction = direction

    def update_screen_dimensions(self, width: int, height: int) -> None:
        """Update screen dimensions and recalculate minimap size."""
        self.screen_width = width
        self.screen_height = height
        self.minimap_size = min(15, self.screen_height // 3, self.screen_width // 4)
        self.minimap_radius = self.minimap_size // 2
        self.x_offset = 1
        self.y_offset = 1

    def render(
        self,
        pixels: list[Pixel],
        center_y: int,
        center_x: int,
        explored_pixels: list[Pixel],
    ) -> list[Pixel]:
        """Generate minimap pixels."""
        explored_map = {(p.y, p.x): p for p in explored_pixels}
        half = self.minimap_size // 2

        if (
            self.x_offset < 0
            or self.x_offset + self.minimap_size + 2 > self.screen_width
        ):
            return pixels

        self._draw_background(pixels)
        self._draw_border(pixels)
        self._draw_cells(pixels, center_y, center_x, explored_map, half)

        return pixels

    def _draw_background(self, pixels: list[Pixel]) -> None:
        """Draw black background for minimap."""
        for dy in range(self.minimap_size + 2):
            y_pixel = self.y_offset + dy
            for dx in range(self.minimap_size + 2):
                x_pixel = self.x_offset + dx
                if (
                    0 <= y_pixel < self.screen_height
                    and 0 <= x_pixel < self.screen_width
                ):
                    pixels.append(Pixel(y_pixel, x_pixel, " ", COLORS.BLACK))

    def _draw_border(self, pixels: list[Pixel]) -> None:
        """Draw border around minimap."""
        border_color = COLORS.PERVANCHE
        for dy in range(self.minimap_size + 2):
            y_pixel = self.y_offset + dy
            for dx in range(self.minimap_size + 2):
                x_pixel = self.x_offset + dx
                if (
                    0 <= y_pixel < self.screen_height
                    and 0 <= x_pixel < self.screen_width
                ):
                    if (
                        dy == 0
                        or dy == self.minimap_size + 1
                        or dx == 0
                        or dx == self.minimap_size + 1
                    ):
                        pixels.append(Pixel(y_pixel, x_pixel, "+", border_color))

    def _draw_cells(
        self,
        pixels: list[Pixel],
        center_y: int,
        center_x: int,
        explored_map: dict,
        half: int,
    ) -> None:
        """Draw cells on minimap with rotation."""
        for dy in range(-half, half + 1):
            mini_y = half + dy
            for dx in range(-half, half + 1):
                rotated_dy, rotated_dx = self._rotate_offset(dy, dx)

                world_y = center_y + rotated_dy
                world_x = center_x + rotated_dx

                mini_x = half + dx

                if (
                    not 0 <= mini_y < self.minimap_size
                    or not 0 <= mini_x < self.minimap_size
                ):
                    continue

                x_pixel = self.x_offset + mini_x + 1
                y_pixel = self.y_offset + mini_y + 1

                if (
                    0 <= y_pixel < self.screen_height
                    and 0 <= x_pixel < self.screen_width
                ):
                    if (world_y, world_x) in explored_map:
                        pixel = explored_map[world_y, world_x]
                        if world_y == center_y and world_x == center_x:
                            pixels.append(Pixel(y_pixel, x_pixel, "^", COLORS.YELLOW))
                        else:
                            pixels.append(
                                Pixel(y_pixel, x_pixel, pixel.content, pixel.color)
                            )
                    else:
                        pixels.append(Pixel(y_pixel, x_pixel, " ", COLORS.BLACK))

    def _rotate_offset(self, dy: int, dx: int) -> tuple[int, int]:
        """
        Rotate global offset so view direction points up.
        direction: 0=east, 1=south, 2=west, 3=north
        """
        if self.direction == 2:
            return (-dx, dy)
        if self.direction == 1:
            return (-dy, -dx)
        if self.direction == 0:
            return (dx, -dy)
        return (dy, dx)
