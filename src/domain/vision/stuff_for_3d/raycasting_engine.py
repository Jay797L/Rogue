"""Module for raycasting engine in pseudo-3D view."""

import math
from typing import Any

from domain.base.core.pixel import Pixel
from domain.base.data.colors import COLORS
from domain.base.utils.point import Point
from domain.map.map_assembly.map_manager import MapManager


class RaycastingEngine:
    """Handles raycasting for pseudo-3D rendering."""

    def __init__(
        self, map_manager: MapManager, character_of_view: Any, max_render_dist: int = 20
    ):
        self.map_manager = map_manager
        self.character_of_view = character_of_view
        self.max_render_dist = max_render_dist

        self.wall_textures = {
            "#": [
                "▓▓▒▒▓▓▒",
                "▓▒▓▒▓▒▓",
                "▒▓▒▓▒▓▒",
                "▓▓▒▒▓▓▒",
                "▒▓▒▓▒▓▒",
                "▓▒▓▒▓▒▓",
                "▓▓▒▒▓▓▒",
                "▒▓▒▓▒▓▒",
            ],
            "D": [
                "███████",
                "█     █",
                "█  █  █",
                "█  █  █",
                "█  █  █",
                "█     █",
                "█     █",
                "███████",
            ],
            "E": [
                "███████",
                "█░░░░░█",
                "█░EEE░█",
                "█░EEE░█",
                "█░EEE░█",
                "█░░░░░█",
                "███████",
                "███████",
            ],
            "^": [
                "┌───┐",
                "│ ^ │",
                "│ ^ │",
                "│ ^ │",
                "│ ^ │",
                "└───┘",
                "░░░░░",
                "░░░░░",
            ],
            "?": [
                "┌───┐",
                "│?│?│",
                "│?│?│",
                "│?│?│",
                "│?│?│",
                "└───┘",
                "░░░░░",
                "░░░░░",
            ],
            "&": [
                "┌───┐",
                "│ /│",
                "│/ │",
                "│ \\│",
                "│\\ │",
                "└───┘",
                "░░░░░",
                "░░░░░",
            ],
            "$": [
                "█████",
                "█$$$█",
                "█$$$█",
                "█$$$█",
                "█$$$█",
                "█████",
                "░░░░░",
                "░░░░░",
            ],
        }
        self.default_texture = [
            "▓▓▒▒▓▓▒",
            "▓▒▓▒▓▒▓",
            "▒▓▒▓▒▓▒",
            "▓▓▒▒▓▓▒",
            "▒▓▒▓▒▓▒",
            "▓▒▓▒▓▒▓",
            "▓▓▒▒▓▓▒",
            "▒▓▒▓▒▓▒",
        ]

    def cast_ray(self, py: float, px: float, angle: float) -> tuple[float, str, Any]:
        """DDA ray casting, returns (distance_to_wall, wall_symbol, nearest_entity). Entities do not block."""
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)

        map_x = int(px)
        map_y = int(py)

        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (px - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - px) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (py - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - py) * delta_dist_y

        hit = False
        side = 0
        nearest_entity = None
        nearest_entity_distance = float("inf")
        wall_distance = self.max_render_dist
        wall_symbol = " "

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if map_x < 0 or map_y < 0 or map_x > 1000 or map_y > 1000:
                break

            point = Point(map_y, map_x)
            cell = self.map_manager[point]

            # Check for entity – remember nearest, but do NOT stop the ray
            if (
                cell is not None
                and cell.owner is not None
                and cell.owner != self.character_of_view
            ):
                entity = cell.owner
                if side == 0:
                    dist = side_dist_x - delta_dist_x
                else:
                    dist = side_dist_y - delta_dist_y
                if dist < nearest_entity_distance:
                    nearest_entity_distance = dist
                    nearest_entity = entity

            # Check for wall – stop the ray here
            if cell is not None and self._is_wall(cell):
                hit = True
                if side == 0:
                    wall_distance = side_dist_x - delta_dist_x
                else:
                    wall_distance = side_dist_y - delta_dist_y
                wall_symbol = cell.content if hasattr(cell, "content") else "#"
                break

        # Return wall info (distance and symbol) and the nearest entity (may be None)
        return wall_distance, wall_symbol, nearest_entity

    def render_column(
        self,
        pixels: list[Pixel],
        col: int,
        distance: float,
        wall_type: str,
        screen_width: int,
        screen_height: int,
    ) -> None:
        """Render a single column of the 3D view."""
        if distance <= 0:
            distance = 0.001

        # If no wall (wall_type is space) and distance is max, draw sky/floor
        if wall_type == " " and distance >= self.max_render_dist - 0.1:
            for row in range(screen_height):
                if row < screen_height // 2:
                    pixels.append(Pixel(row, col, " ", COLORS.BLACK))
                else:
                    pixels.append(Pixel(row, col, ".", COLORS.BLACK))
            return

        wall_height = int(screen_height / distance * 0.8)
        wall_height = min(wall_height, screen_height)

        texture = self.wall_textures.get(wall_type, self.default_texture)
        texture_height = len(texture)
        texture_width = max(len(line) for line in texture) if texture else 8

        y_offset = (screen_height - wall_height) // 2

        for row in range(screen_height):
            if y_offset <= row < y_offset + wall_height:
                is_door = wall_type in {"D", "k"}

                if is_door:
                    if wall_height > 1:
                        relative_y = (row - y_offset) / (wall_height - 1)
                    else:
                        relative_y = 0.5
                    texture_y = int(relative_y * (texture_height - 1))
                    texture_y = max(0, min(texture_y, texture_height - 1))

                    if screen_width > 1:
                        relative_x = col / (screen_width - 1)
                    else:
                        relative_x = 0.5
                    texture_x = int(relative_x * (texture_width - 1))
                    texture_x = max(0, min(texture_x, texture_width - 1))
                else:
                    texture_y = (row - y_offset) % texture_height
                    texture_x = col % texture_width

                texture_line = texture[texture_y]
                if texture_x < len(texture_line):
                    symbol = texture_line[texture_x]
                else:
                    symbol = texture_line[0]

                intensity = max(0, 1.0 - distance / self.max_render_dist)
                color = self._get_color_by_distance(intensity)
                pixels.append(Pixel(row, col, symbol, color))
            elif row < screen_height // 2:
                pixels.append(Pixel(row, col, " ", COLORS.BLACK))
            else:
                pixels.append(Pixel(row, col, ".", COLORS.BLACK))

    @staticmethod
    def _is_wall(cell) -> bool:
        """Check if cell blocks vision. Only solid walls and closed doors block."""
        if hasattr(cell, "blocking_vision") and cell.blocking_vision:
            return True
        # Solid walls and closed doors block; items and enemies do not
        return cell.content in {"#", "█", "D"}

    @staticmethod
    def _get_entity_symbol(entity) -> str:
        """Get symbol for entity."""
        if hasattr(entity, "name"):
            name = entity.name.lower()
            if "player" in name:
                return "@"
            if "zombie" in name:
                return "Z"
            if "ghost" in name:
                return "G"
            if "ogr" in name:
                return "O"
            if "snake_mage" in name or "snake" in name:
                return "S"
            if "vampire" in name:
                return "V"
            if "mimik" in name:
                return "M"
            if "key" in name:
                return "k"
        return "?"

    @staticmethod
    def _get_color_by_distance(intensity: float) -> int:
        """Get color based on distance intensity."""
        if intensity > 0.8:
            return COLORS.WHITE
        if intensity > 0.5:
            return COLORS.PERVANCHE
        if intensity > 0.2:
            return COLORS.BLUE
        return COLORS.BLACK
