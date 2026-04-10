import contextlib
import curses
import logging

from domain.base.core.base_game import BaseGame
from domain.base.core.base_item import Item
from domain.base.core.item_category import ItemCategory
from domain.base.data import STRINGS
from domain.game.states.inventory_state import InventoryState

from .color_manager import ColorPreset, color_manager

logger = logging.getLogger(__name__)


class InventoryRenderer:
    """Рендерер инвентаря в стиле ASCII-арт."""

    def _item_art(self, item):
        """Возвращает матрицу символов 5x5 для предмета."""
        # Сначала проверяем, есть ли у предмета свой арт
        if hasattr(item, "art") and item.art:
            # Приводим к списку строк, если это tuple
            art = list(item.art) if isinstance(item.art, tuple) else item.art
            # Убеждаемся что арт имеет размер 5x5 или масштабируем
            if len(art) == 5 and all(len(line) == 5 for line in art):
                return art

        # Если своего арта нет, используем стандартный по категории
        if item.category == ItemCategory.EAT:
            return ["  █  ", " ███ ", "█████", "█████", " ███ "]
        elif item.category == ItemCategory.ELIXIR:
            return ["  █  ", " ███ ", " █ █ ", " █ █ ", " ███ "]
        elif item.category == ItemCategory.SCROLL:
            return ["█████", "█   █", "█   █", "█   █", "█████"]
        elif item.category == ItemCategory.WEAPON:
            return ["  █  ", "  █  ", " ███ ", "█   █", "  █  "]
        else:
            return ["     ", "     ", "  ?  ", "     ", "     "]

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.cell_width = 7
        self.cells_count = 9
        self.grid_width = self.cells_count * self.cell_width + 1
        self.left_part_width = 4
        self.right_part_width = 10
        self.total_width = (
            self.left_part_width + self.grid_width + self.right_part_width
        )
        self.title = STRINGS.INVENTORY_TITLE
        self.numbers_line = " " * self.left_part_width + "".join(
            str(i).center(self.cell_width) for i in range(1, 10)
        )

    def render(self, game: BaseGame):
        """Отрисовать инвентарь поверх карты, не закрывая панель статистики и сообщения."""
        height, width = self.stdscr.getmaxyx()

        stats_width = 29
        right_panel_x = width - stats_width

        map_start_x = 2
        map_end_x = right_panel_x - 2
        map_width = map_end_x - map_start_x + 1

        start_y = max(2, (height - 26) // 2)
        start_x = map_start_x + max(0, (map_width - self.total_width) // 2)

        for y in range(start_y - 1, start_y + 26):
            if y < height:
                with contextlib.suppress(curses.error):
                    self.stdscr.addstr(y, map_start_x, " " * map_width)

        title_x = start_x + (self.total_width - len(self.title)) // 2
        title_color = color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
        try:
            self.stdscr.addstr(
                start_y,
                title_x,
                self.title,
                curses.A_BOLD | curses.color_pair(title_color),
            )
        except curses.error:
            pass

        current_y = start_y + 1
        state = game.fsm.current_state_instance

        for row in range(4):
            if row == 0:
                items = game.player.backpack.eat
                category_name = f" {STRINGS.CATEGORY_EAT.value}"
            elif row == 1:
                items = game.player.backpack.elixirs
                category_name = f" {STRINGS.CATEGORY_ELIXIR.value}"
            elif row == 2:
                items = game.player.backpack.scrolls
                category_name = f" {STRINGS.CATEGORY_SCROLL.value}"
            else:
                items = game.player.backpack.weapon
                category_name = f" {STRINGS.CATEGORY_WEAPON.value}"

            left_char = (
                state.inventory_keys[row] if row < len(state.inventory_keys) else " "
            )
            is_category_selected = state.inventory_pointer == row
            attr_right = (
                curses.A_BOLD
                | curses.color_pair(
                    color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
                )
                if is_category_selected
                else 0
            )

            for line_in_cat in range(7):
                y = current_y + line_in_cat
                if y >= height:
                    break

                left_part = f" {left_char} " if line_in_cat == 3 else "   "
                self.stdscr.addstr(y, start_x, left_part)

                for slot_index in range(9):
                    item = items[slot_index] if slot_index < len(items) else None

                    # Проверяем, экипировано ли это оружие
                    is_equipped_weapon = (
                        row == 3  # категория оружия
                        and item is not None
                        and hasattr(game.player.backpack, "equipped_weapon_index")
                        and slot_index + 1 == game.player.backpack.equipped_weapon_index
                    )

                    # Проверяем, выбран ли этот слот
                    is_slot_selected = (
                        state.selected_slot_index is not None
                        and slot_index + 1 == state.selected_slot_index
                        and row == state.inventory_pointer
                    )

                    # Определяем атрибуты цвета для ячейки
                    if is_slot_selected:
                        # Выбранный слот - желтый
                        attr_cell = curses.A_BOLD | curses.color_pair(
                            color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
                        )
                    elif is_equipped_weapon:
                        # Экипированное оружие - красный
                        attr_cell = curses.A_BOLD | curses.color_pair(
                            color_manager.get_color_pair_from_preset(ColorPreset.RED)
                        )
                    else:
                        # Обычная ячейка
                        attr_cell = 0

                    cell_chars = []
                    for col_in_cell in range(7):
                        is_vertical_border = col_in_cell in {0, 6}
                        is_horizontal_border = line_in_cat in {0, 6}
                        if is_vertical_border or is_horizontal_border:
                            cell_chars.append(".")
                            continue
                        inner_row = line_in_cat - 1
                        inner_col = col_in_cell - 1
                        if item is not None:
                            # 🔥 ВСЕГДА используем арт предмета, если он есть
                            art = self._item_art(item)
                            if (
                                art
                                and 0 <= inner_row < len(art)
                                and 0 <= inner_col < len(art[0])
                            ):
                                cell_chars.append(art[inner_row][inner_col])
                            elif line_in_cat == 3 and col_in_cell == 2:
                                # Символ только если арта нет или для центральной позиции
                                sym = self._item_symbol(item)

                                if is_equipped_weapon:
                                    sym = "+"
                                cell_chars.append(sym)
                            else:
                                cell_chars.append(" ")
                        else:
                            cell_chars.append(" ")
                    cell_line = "".join(cell_chars)

                    x_cell = (
                        start_x + self.left_part_width + slot_index * self.cell_width
                    )
                    self.stdscr.addstr(y, x_cell, cell_line, attr_cell)

                right_part = category_name.ljust(self.right_part_width)
                self.stdscr.addstr(
                    y,
                    start_x + self.left_part_width + self.grid_width,
                    right_part,
                    attr_right,
                )

            current_y += 7

        if current_y + 1 < height:
            try:
                self.stdscr.addstr(current_y, start_x, self.numbers_line)
            except curses.error:
                pass
        current_y += 1

        treasure_line = STRINGS.TREASURE_LABEL.format(game.player.backpack.treasure)
        if current_y < height:
            treasure_color = color_manager.get_color_pair_from_preset(
                ColorPreset.BRIGHT_TEXT
            )
            try:
                self.stdscr.addstr(
                    current_y,
                    start_x + self.left_part_width,
                    treasure_line,
                    curses.A_BOLD | curses.color_pair(treasure_color),
                )
            except curses.error:
                pass
        current_y += 1

        help_line = STRINGS.INVENTORY_HELP
        if current_y < height:
            help_color = color_manager.get_color_pair_from_preset(ColorPreset.DIM_TEXT)
            try:
                self.stdscr.addstr(
                    current_y,
                    start_x + self.left_part_width,
                    help_line,
                    curses.A_DIM | curses.color_pair(help_color),
                )
            except curses.error:
                pass

        info_panel_start_x = max(1, start_x - 32)
        self._draw_info_panel(game, start_y, info_panel_start_x)

    def _item_symbol(self, item: Item):
        if item.category.value == ItemCategory.EAT.value:
            return "f"
        elif item.category.value == ItemCategory.ELIXIR.value:
            return "!"
        elif item.category.value == ItemCategory.SCROLL.value:
            return "?"
        elif item.category.value == ItemCategory.WEAPON.value:
            return "/"
        else:
            return "?"

    def _draw_info_panel(self, game: BaseGame, start_y: int, start_x: int) -> None:
        """Рисует информационное окно слева от инвентаря."""
        state = game.fsm.current_state_instance
        if not isinstance(state, InventoryState) or state.last_selected_item is None:
            return

        item = state.last_selected_item
        panel_width = 30
        panel_height = 20
        panel_x = start_x
        panel_y = start_y

        max_y, max_x = self.stdscr.getmaxyx()
        if (
            panel_x < 0
            or panel_y < 0
            or panel_x + panel_width > max_x
            or panel_y + panel_height > max_y
        ):
            logger.debug("Info panel does not fit, skipping")
            return

        try:
            self.stdscr.addstr(panel_y, panel_x, "+" + "-" * (panel_width - 2) + "+")
            for i in range(1, panel_height - 1):
                self.stdscr.addstr(panel_y + i, panel_x, "|")
                self.stdscr.addstr(panel_y + i, panel_x + panel_width - 1, "|")
            self.stdscr.addstr(
                panel_y + panel_height - 1, panel_x, "+" + "-" * (panel_width - 2) + "+"
            )
        except curses.error:
            logger.debug("Failed to draw panel border")
            return

        try:
            parts = item.name.split()
            for i, part in enumerate(parts):
                y = panel_y + 2 + i
                text = f"  {part}"
                highlight_color = curses.color_pair(
                    color_manager.get_color_pair_from_preset(ColorPreset.YELLOW)
                )
                self.stdscr.addstr(
                    y, panel_x + 2, text, curses.A_BOLD | highlight_color
                )

            # 🔥 Показываем арт предмета в панели информации
            if hasattr(item, "art") and item.art:
                art_to_show = item.art
                if isinstance(art_to_show, tuple):
                    art_to_show = list(art_to_show)
                for i, part in enumerate(art_to_show):
                    y = panel_y + 2 + i
                    highlight_color = curses.color_pair(
                        color_manager.get_color_pair_from_preset(ColorPreset.RED)
                    )
                    self.stdscr.addstr(
                        y, panel_x + 18, part, curses.A_BOLD | highlight_color
                    )

            spec_y = panel_y + 11
            spec_text = f"  {item.specification}"
            if len(spec_text) > panel_width - 4:
                spec_text = spec_text[: panel_width - 4]
            self.stdscr.addstr(spec_y, panel_x + 2, spec_text)

            half = panel_width // 2
            use_abort_y = panel_y + panel_height - 4
            left_part = "  USE".ljust(half - 1)
            right_part = "ABORT  ".rjust(half - 1)
            self.stdscr.addstr(use_abort_y, panel_x + 1, left_part + right_part)

            help_y = panel_y + panel_height - 3
            left_help = "  Enter".ljust(half - 1)
            right_help = "Backspace".rjust(half - 1)
            dim_color = curses.color_pair(
                color_manager.get_color_pair_from_preset(ColorPreset.DIM_TEXT)
            )
            self.stdscr.addstr(
                help_y, panel_x + 1, left_help + right_help, curses.A_DIM | dim_color
            )

        except curses.error:
            logger.debug("Failed to draw panel content")

    def _get_cell_line(
        self, item, line_in_cat: int, slot_index: int, col_in_cell_range=range(7)
    ) -> str:
        """Возвращает строку из 7 символов для одной строки ячейки."""
        chars = []
        for col_in_cell in col_in_cell_range:
            is_vertical_border = col_in_cell in {0, 6}
            is_horizontal_border = line_in_cat in {0, 6}
            if is_vertical_border or is_horizontal_border:
                chars.append(".")
                continue
            inner_row = line_in_cat - 1
            inner_col = col_in_cell - 1
            if item is not None:
                art = self._item_art(item)
                if art and 0 <= inner_row < len(art) and 0 <= inner_col < len(art[0]):
                    chars.append(art[inner_row][inner_col])
                elif line_in_cat == 3 and col_in_cell == 2:
                    sym = self._item_symbol(item)
                    chars.append(sym)
                else:
                    chars.append(" ")
            else:
                chars.append(" ")
        return "".join(chars)
