"""Состояние инвентаря."""

from domain.base.core.base_item import Item
from domain.base.core.item_category import ItemCategory
from domain.base.data.entities.player import equip_weapon, unequip_weapon
from domain.base.data.strings import STRINGS
from domain.base.utils.point import Point
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase


class InventoryState(GameStateBase):
    """Состояние инвентаря."""

    CAT_EAT = 0
    CAT_ELIXIR = 1
    CAT_SCROLL = 2
    CAT_WEAPON = 3

    def __init__(self, game):
        super().__init__(game)
        self.inventory_pointer = self.CAT_EAT
        self.inventory_categories = [
            STRINGS.CATEGORY_EAT,
            STRINGS.CATEGORY_ELIXIR,
            STRINGS.CATEGORY_SCROLL,
            STRINGS.CATEGORY_WEAPON,
        ]
        self.inventory_keys = ["A", "S", "D", "F"]
        self.selected_slot_index: int | None = None
        self.last_selected_item = None
        self._previous_state = None

    def handle_input(self, action: GameKey) -> bool:
        """Обработка ввода в инвентаре."""

        if hasattr(self, "_processing") and self._processing:
            return True

        if action in (
            GameKey.KEY_W,
            GameKey.KEY_S,
            GameKey.KEY_A,
            GameKey.KEY_D,
            GameKey.KEY_F,
        ):
            self.selected_slot_index = None
            self.last_selected_item = None

        if action == GameKey.KEY_A:
            self.inventory_pointer = self.CAT_EAT
            return True
        if action == GameKey.KEY_S:
            self.inventory_pointer = self.CAT_ELIXIR
            return True
        if action == GameKey.KEY_D:
            self.inventory_pointer = self.CAT_SCROLL
            return True
        if action == GameKey.KEY_F:
            self.inventory_pointer = self.CAT_WEAPON
            return True

        if action in (
            GameKey.NUM_1,
            GameKey.NUM_2,
            GameKey.NUM_3,
            GameKey.NUM_4,
            GameKey.NUM_5,
            GameKey.NUM_6,
            GameKey.NUM_7,
            GameKey.NUM_8,
            GameKey.NUM_9,
        ):
            slot = self._get_slot_from_action(action)
            if slot is not None:
                self.selected_slot_index = slot
                items = self._get_category_items()
                if 1 <= slot <= len(items):
                    self.last_selected_item = items[slot - 1]
                else:
                    self.last_selected_item = None
            return True

        if action == GameKey.SELECT:
            if self.selected_slot_index is not None:
                self._processing = True
                try:
                    if self.inventory_pointer == self.CAT_WEAPON:
                        self._equip_weapon_from_slot(self.selected_slot_index)
                    else:
                        self._use_item_from_slot_by_index(self.selected_slot_index)
                finally:
                    self._processing = False
                self.selected_slot_index = None
                self.last_selected_item = None
            return True

        if action == GameKey.BACKSPACE:
            if self.selected_slot_index is not None:
                self._drop_item_from_slot(self.selected_slot_index)
                self.selected_slot_index = None
                self.last_selected_item = None
            return True

        if action == GameKey.INVENTORY:
            if self.game.fsm._previous_state == GameState.EXPLORING_3D:
                if not self.game.is_3d_mode:
                    self.game.switch_vision_mode(True)
                self.game.fsm.transition_to(GameState.EXPLORING_3D)
            else:
                self.game.fsm.transition_to(GameState.EXPLORING)
            return True

        if action == GameKey.KEY_Q:
            self.game.save_game(is_auto=True)
            self.game.message = STRINGS.RETURN_TO_MENU
            self.game.fsm.transition_to(GameState.MENU)
            return True

        if action == GameKey.NUM_0:
            if self.inventory_pointer == self.CAT_WEAPON:
                self._unequip_weapon()
            return True

        return True

    def _unequip_weapon(self):
        old_weapon = self.game.player.backpack.equip_weapon(0)
        if old_weapon:
            if (
                len(self.game.player.backpack.weapon)
                < self.game.player.backpack.max_capacity
            ):
                self.game.player.backpack.weapon.append(old_weapon)
                self.game.message = STRINGS.WEAPON_UNEQUIPPED.format(old_weapon.name)
            else:
                drop_pos = self._get_nearest_empty_cell()
                if drop_pos:
                    point = Point(drop_pos[0], drop_pos[1])
                    old_weapon.point = point
                    self.game.level.map_manager[point] = old_weapon.cell
                    self.game.message = STRINGS.WEAPON_DROPPED.format(old_weapon.name)
                else:
                    self.game.message = STRINGS.WEAPON_LOST.format(old_weapon.name)
        else:
            self.game.message = STRINGS.NO_WEAPON_EQUIPPED

    def _use_item_from_slot(self, action: GameKey) -> bool:
        """Использовать предмет из выбранного слота."""
        slot_index = self._get_slot_from_action(action)
        if slot_index is None:
            return True

        items = self._get_category_items()

        if 1 <= slot_index <= len(items):
            item = items[slot_index - 1]
            self._use_item(item)

        else:
            self.game.message = STRINGS.SLOT_EMPTY.format(slot_index)

        return True

    @staticmethod
    def _get_slot_from_action(action: GameKey) -> int | None:
        """Получить номер слота из действия."""
        slot_map = {
            GameKey.NUM_1: 1,
            GameKey.NUM_2: 2,
            GameKey.NUM_3: 3,
            GameKey.NUM_4: 4,
            GameKey.NUM_5: 5,
            GameKey.NUM_6: 6,
            GameKey.NUM_7: 7,
            GameKey.NUM_8: 8,
            GameKey.NUM_9: 9,
        }
        return slot_map.get(action)

    def _get_category_items(self) -> list[Item]:
        """Получить предметы текущей категории."""
        if self.inventory_pointer == self.CAT_EAT:
            return self.game.player.backpack.eat
        if self.inventory_pointer == self.CAT_ELIXIR:
            return self.game.player.backpack.elixirs
        if self.inventory_pointer == self.CAT_SCROLL:
            return self.game.player.backpack.scrolls
        if self.inventory_pointer == self.CAT_WEAPON:
            return self.game.player.backpack.weapon
        return []

    def _use_item(self, item: Item):
        """Применить эффект предмета."""
        self.game.message = STRINGS.ITEM_USED.format(item.name, item.specification)
        items = self._get_category_items()
        effect = item.action.to_target(self.game.player).build()
        items.remove(item)
        self.game.level.enemy_manager.active_effects.append(effect)

        if item.category == ItemCategory.EAT:
            self.game.statistics.record_food_eaten()
        elif item.category == ItemCategory.ELIXIR:
            self.game.statistics.record_elixir_drank()
        elif item.category == ItemCategory.SCROLL:
            self.game.statistics.record_scroll_read()
        elif item.category == ItemCategory.WEAPON:
            self.game.statistics.record_weapon_used()

    def _use_item_from_slot_by_index(self, slot_index: int) -> bool:
        """Использовать предмет по индексу слота в текущей категории."""
        items = self._get_category_items()
        if 1 <= slot_index <= len(items):
            item = items[slot_index - 1]
            self._use_item(item)
            return True
        self.game.message = STRINGS.SLOT_EMPTY.format(slot_index)
        return False

    def _get_nearest_empty_cell(self):
        """Возвращает координаты (y, x) ближайшей пустой клетки к игроку."""
        player = self.game.player
        if not hasattr(self.game, "level") or not self.game.level:
            return None
        py = player.point.y
        px = player.point.x
        min_dist = float("inf")
        best_cell = None
        for y in range(py - 5, py + 6):
            for x in range(px - 5, px + 6):
                if self.game.level.map_manager.is_empty(Point(y, x)):
                    dist = abs(y - py) + abs(x - px)
                    if dist < min_dist:
                        min_dist = dist
                        best_cell = (y, x)
        return best_cell

    def _drop_item_from_slot(self, slot_index: int) -> bool:
        """Выкинуть предмет из указанного слота на ближайшую пустую клетку."""
        items = self._get_category_items()
        if not (1 <= slot_index <= len(items)):
            self.game.message = STRINGS.SLOT_EMPTY_DROP.format(slot_index)
            return False

        item = items[slot_index - 1]
        empty_cell = self._get_nearest_empty_cell()
        if empty_cell is None:
            self.game.message = STRINGS.NO_SPACE_TO_DROP
            return False

        items.remove(item)
        point = Point(empty_cell[0], empty_cell[1])
        item.point = point
        self.game.level.map_manager[point] = item.cell
        self.game.message = STRINGS.ITEM_DROPPED.format(item.name)
        return True

    def on_enter(self):
        """При входе в инвентарь."""

        self._previous_state = self.game.fsm.current_state
        self.inventory_pointer = self.CAT_EAT
        self.selected_slot_index = None
        self.last_selected_item = None
        self.game.message = STRINGS.INVENTORY_OPEN

    def on_exit(self):
        """При выходе из инвентаря."""
        self.game.message = STRINGS.INVENTORY_CLOSED

    def _equip_weapon_from_slot(self, slot_index: int) -> bool:
        """Экипировать оружие из указанного слота."""
        items = self._get_category_items()
        unequip_effect = unequip_weapon(self.game.player)
        if unequip_effect:
            self.game.level.enemy_manager.active_effects.append(unequip_effect)
        if 1 <= slot_index <= len(items):
            equip_effect = equip_weapon(self.game.player, items[slot_index - 1])
            if equip_effect:
                self.game.level.enemy_manager.active_effects.append(equip_effect)
        return True
