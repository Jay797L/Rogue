import random

from domain.base.core.item_category import ItemCategory
from domain.base.data.register_item import (
    get_all_items,
    get_items_by_category,
)


def select_random_item() -> type:
    """
    Выбирает случайный предмет с учётом весовых коэффициентов по категориям.

    Шансы:
    - Еда (EAT): 50%
    - Зелья (ELIXIR): 30%
    - Свитки (SCROLL): 15%
    - Оружие (WEAPON): 5%
    - Сокровища (TREASURE): 0% (не спавнятся случайно)

    Returns:
        Класс предмета
    """
    category_weights = {
        ItemCategory.EAT: 50,
        ItemCategory.ELIXIR: 30,
        ItemCategory.SCROLL: 15,
        ItemCategory.WEAPON: 5,
    }

    available_categories = []
    weights = []

    for category, weight in category_weights.items():
        items = get_items_by_category(category)
        if items:
            available_categories.append(category)
            weights.append(weight)

    if not available_categories:
        all_items = get_all_items()
        return random.choice(all_items) if all_items else None

    selected_category = random.choices(available_categories, weights=weights, k=1)[0]

    items_in_category = get_items_by_category(selected_category)
    return random.choice(items_in_category)


def select_item_by_category(category: ItemCategory):
    """Выбирает случайный предмет из указанной категории."""
    items_in_category = get_items_by_category(category)
    if not items_in_category:
        return None
    return random.choice(items_in_category)


def get_category_stats() -> dict:
    """Возвращает статистику по количеству предметов в каждой категории."""
    stats = {}
    for category in ItemCategory:
        items = get_items_by_category(category)
        stats[category.value] = len(items)
    return stats


if __name__ == "__main__":
    from collections import Counter

    print("Регистрация предметов...")
    print(f"Всего предметов: {len(get_all_items())}")
    print("Статистика по категориям:")
    for category, count in get_category_stats().items():
        print(f"  {category}: {count} предметов")

    print("\nТестирование распределения выбора (1000 итераций):")
    results = Counter()
    category_results = Counter()

    for _ in range(1000):
        item_class = select_random_item()
        if item_class and hasattr(item_class, "category"):
            category_results[item_class.category.value] += 1
            results[item_class.__name__] += 1

    print("\nРаспределение по категориям:")
    for category in ["eat", "elixirs", "scrolls", "weapon"]:
        count = category_results[category]
        print(f"  {category}: {count} ({count / 10:.1f}%)")

    print("\nТоп-10 самых частых предметов:")
    for item_name, count in results.most_common(10):
        print(f"  {item_name}: {count} ({count / 10:.1f}%)")
