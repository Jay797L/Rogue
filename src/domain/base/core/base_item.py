from dataclasses import dataclass

from domain.base.core.entity import Entity
from domain.base.core.item_category import ItemCategory


@dataclass(eq=False, frozen=False)
class Item(Entity):
    category: ItemCategory = ItemCategory.TREASURE
    specification: str = "Nothing Effect"
    attribute: str = ""
    art: tuple[str, ...] = ("", "")

    def __post_init__(self):
        super().__post_init__()
        if hasattr(self, "action"):
            if hasattr(self.action, "from_caster"):
                self.action.from_caster(self)
            if hasattr(self.action, "by_attribut"):
                self.action.by_attribut(self.attribute)
            if hasattr(self.action, "by_strength"):
                self.action.by_strength(self.strength)
