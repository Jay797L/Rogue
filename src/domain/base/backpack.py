from domain.base.core.base_item import Item
from domain.base.core.item_category import ItemCategory


class Backpack:
    def __init__(self):
        self.eat: list[Item] = []
        self.elixirs: list[Item] = []
        self.scrolls: list[Item] = []
        self.weapon: list[Item] = []
        self.treasure: int = 0
        self.max_capacity = 9
        self.equipped_weapon_index = 0

    def enough_space(self, item: Item) -> bool:
        if item.category == ItemCategory.TREASURE:
            return True
        pocket = getattr(self, item.category.value)
        return len(pocket) < self.max_capacity

    def add_equipment(self, item: Item) -> None | Item:
        if item.category != ItemCategory.TREASURE:
            return_item = None
            pocket: list = getattr(self, item.category.value)
            if len(pocket) >= self.max_capacity:
                return_item = pocket.pop()
            pocket.append(item)
            return return_item
        self.treasure += item.strength

    def remove_equipment(self, category: ItemCategory, index: int):
        """Удалить предмет из рюкзака."""
        pocket: list = getattr(self, category.value)
        if len(pocket) >= index:
            return pocket.pop(index)

    def equip_weapon(self, index: int) -> Item | None:
        """
        Экипировать оружие из инвентаря по индексу (1..len(weapon)).
        Возвращает ранее экипированное оружие (если было), чтобы выбросить его на пол.
        Если index == 0, то снимаем текущее оружие (голые руки).
        """
        old_weapon = None
        if self.equipped_weapon_index != 0:
            old_weapon = self.weapon[self.equipped_weapon_index - 1]

        if index == 0:
            self.equipped_weapon_index = 0
            return old_weapon

        if 1 <= index <= len(self.weapon):
            self.equipped_weapon_index = index
            return old_weapon
        return None

    def get_attack_strength(self, base_strength: int) -> int:
        """Возвращает общую силу атаки с учётом экипированного оружия."""
        if self.equipped_weapon_index == 0:
            return base_strength
        weapon = self.weapon[self.equipped_weapon_index - 1]
        return base_strength + weapon.strength
