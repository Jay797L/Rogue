"""Модуль для анимированного ASCII‑арта (виджеты, трансформации, цвета)."""

import contextlib
import curses
import math
import os
import time
from pathlib import Path

from .color_manager import ColorPreset, color_manager

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"


class Art:
    """Хранит ASCII‑арт как список строк."""

    def __init__(self, lines: list[str], color_hex: str = ColorPreset.WHITE.value):
        self.lines = lines
        self.height = len(lines)
        self.width = max(len(line) for line in lines) if lines else 0
        self.color_hex = color_hex

    @classmethod
    def from_file(
        cls, filepath: str, color_hex: str = ColorPreset.WHITE.value
    ) -> "Art":
        filepath = os.path.expanduser(f"{ASSETS_DIR}/{filepath}")
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f.readlines()]
        except FileNotFoundError:
            lines = [f"Файл {filepath} не найден"]
        except Exception as e:
            lines = [f"Ошибка: {str(e)}"]
        return cls(lines, color_hex)

    def is_empty(self) -> bool:
        return self.height == 0 or all(not line for line in self.lines)


class TransformParams:
    """Параметры трансформации ASCII‑арта."""

    def __init__(
        self,
        scale_x: int = 100,
        scale_y: int = 100,
        skew: int = 0,
        offset_x: int = 0,
        offset_y: int = 0,
    ):
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.skew = skew
        self.offset_x = offset_x
        self.offset_y = offset_y

    def copy(self) -> "TransformParams":
        return TransformParams(
            self.scale_x, self.scale_y, self.skew, self.offset_x, self.offset_y
        )


class Transformer:
    """Применяет трансформации к Art."""

    @staticmethod
    def _scale_x_line(line: str, scale_x: int) -> str:
        if scale_x == 100 or not line:
            return line
        new_len = max(1, int(len(line) * scale_x / 100))
        if new_len <= len(line):
            step = len(line) / new_len
            return "".join(line[int(i * step)] for i in range(new_len))
        result = []
        for i in range(new_len):
            src_pos = int(i * len(line) / new_len)
            result.append(line[src_pos])
        return "".join(result)

    @staticmethod
    def _scale_y(art: Art, scale_y: int) -> Art:
        if scale_y == 100 or art.is_empty():
            return art
        new_height = max(1, int(art.height * scale_y / 100))
        if new_height <= art.height:
            step = art.height / new_height
            new_lines = [art.lines[int(i * step)] for i in range(new_height)]
        else:
            new_lines = []
            for i in range(new_height):
                src_pos = int(i * art.height / new_height)
                new_lines.append(art.lines[src_pos])
        return Art(new_lines, art.color_hex)

    @staticmethod
    def _skew_line(line: str, line_idx: int, skew: int, base_offset: int = 0) -> str:
        if skew == 0:
            return line
        offset = int(line_idx * skew / 100) + base_offset
        if offset > 0:
            return " " * offset + line
        if offset < 0:
            return line[-offset:]
        return line

    @classmethod
    def transform(cls, art: Art, params: TransformParams) -> Art:
        if art.is_empty():
            return art
        y_scaled = cls._scale_y(art, params.scale_y)
        transformed_lines = []
        for i, line in enumerate(y_scaled.lines):
            x_scaled = cls._scale_x_line(line, params.scale_x)
            skewed = cls._skew_line(
                x_scaled, i + params.offset_y, params.skew, params.offset_x
            )
            transformed_lines.append(skewed)
        return Art(transformed_lines, art.color_hex)


class Animator:
    """Генерирует параметры трансформации для анимации."""

    def __init__(
        self,
        base_params: TransformParams,
        scale_x_amplitude: int = 0,
        scale_y_amplitude: int = 0,
        skew_amplitude: int = 0,
        circle_radius_x: int = 0,
        circle_radius_y: int = 0,
        speed: float = 0,
    ):
        self.base_params = base_params
        self.scale_x_amplitude = scale_x_amplitude
        self.scale_y_amplitude = scale_y_amplitude
        self.skew_amplitude = skew_amplitude
        self.circle_radius_x = circle_radius_x
        self.circle_radius_y = circle_radius_y
        self.speed = speed
        self.time_offset = time.time()

    def get_params(self, current_time: float) -> TransformParams:
        t = current_time * self.speed + self.time_offset
        offset_x = int(math.sin(t) * self.circle_radius_x)
        offset_y = int(math.cos(t) * self.circle_radius_y)
        scale_x = self.base_params.scale_x + int(
            math.sin(t * 2) * self.scale_x_amplitude
        )
        scale_y = self.base_params.scale_y + int(
            math.cos(t * 1.5) * self.scale_y_amplitude
        )
        skew = self.base_params.skew + int(math.sin(t) * self.skew_amplitude)
        return TransformParams(scale_x, scale_y, skew, offset_x, offset_y)


class Widget:
    def __init__(
        self,
        art: Art,
        y: int,
        x: int,
        selected_params: TransformParams | None = None,
        animator: Animator | None = None,
        color_hex: str = ColorPreset.WHITE.value,
        bg_color_hex: str = "transparent",
    ):
        self.art = art
        self.y = y
        self.x = x
        self.selected_params = selected_params or TransformParams(60, 80, 0, 0, 0)
        self.animator = animator or Animator(TransformParams(40, 60))
        self.is_selected = False
        self.current_params = self.selected_params.copy()
        self.color_hex = color_hex
        self.bg_color_hex = bg_color_hex
        self.selected_color_hex = ColorPreset.YELLOW.value

    def get_current_color(self) -> str:
        return self.selected_color_hex if self.is_selected else self.color_hex

    def select(self):
        self.is_selected = True

    def deselect(self):
        self.is_selected = False

    def update(self, current_time: float):
        if not self.is_selected:
            self.current_params = self.animator.get_params(current_time)
        else:
            self.current_params = self.selected_params.copy()

    def draw(self, stdscr, current_time: float):
        self.update(current_time)
        transformer = Transformer()
        transformed_art = transformer.transform(self.art, self.current_params)
        if transformed_art.is_empty():
            return
        start_y = self.y - transformed_art.height // 2 + self.current_params.offset_y
        start_x = self.x - transformed_art.width // 2 + self.current_params.offset_x
        max_y, max_x = stdscr.getmaxyx()
        color_pair = color_manager.get_color_pair(
            self.get_current_color(), self.bg_color_hex
        )

        if self.is_selected:
            stdscr.attron(curses.A_BOLD)
        stdscr.attron(curses.color_pair(color_pair))

        for i, line in enumerate(transformed_art.lines):
            draw_y = start_y + i
            if draw_y < 0 or draw_y >= max_y:
                continue
            draw_x = start_x
            if draw_x < 0:
                if abs(draw_x) < len(line):
                    line = line[-draw_x:]
                    draw_x = 0
                else:
                    continue
            if draw_x >= max_x:
                continue
            max_len = max_x - draw_x
            if max_len > 0:
                display_line = line[:max_len]
                with contextlib.suppress(curses.error):
                    stdscr.addstr(draw_y, draw_x, display_line)

        stdscr.attroff(curses.color_pair(color_pair))
        if self.is_selected:
            stdscr.attroff(curses.A_BOLD)

        stdscr.attroff(curses.A_BOLD)
        stdscr.attroff(curses.A_REVERSE)
        stdscr.attroff(curses.A_UNDERLINE)
        stdscr.attroff(curses.A_DIM)
