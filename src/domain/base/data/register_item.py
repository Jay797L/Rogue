from domain.base.core.base_item import Item
from domain.base.core.item_category import ItemCategory

ITEMS_BY_NAME: dict[str, type[Item]] = {}
ITEM_REGISTRY: list[type] = []
ITEMS_BY_CATEGORY: dict[ItemCategory, list[type]] = {
    ItemCategory.EAT: [],
    ItemCategory.ELIXIR: [],
    ItemCategory.SCROLL: [],
    ItemCategory.WEAPON: [],
    ItemCategory.TREASURE: [],
}


def register_item_class(cls: type[Item]) -> None:
    """Явно регистрирует класс предмета (вместо декоратора)."""
    ITEM_REGISTRY.append(cls)
    ITEMS_BY_NAME[cls.__name__] = cls
    if hasattr(cls, "category"):
        category = cls.category
        if category in ITEMS_BY_CATEGORY:
            ITEMS_BY_CATEGORY[category].append(cls)


def get_items_by_category(category: ItemCategory) -> list[type]:
    return ITEMS_BY_CATEGORY.get(category, [])


def get_all_items() -> list[type]:
    return ITEM_REGISTRY


def get_item_by_name(name: str) -> type[Item] | None:
    return ITEMS_BY_NAME.get(name)
