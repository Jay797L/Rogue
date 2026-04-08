"""Модуль для генерации графов соединений между комнатами.

Содержит класс GraphGenerator, который создает графы на основе предопределенных масок
соединений.
"""

import random

from domain.base.data.graph_masks import MASKS
from domain.map.map_graph.graph import Graph


class GraphGenerator:
    """Генератор графов соединений между комнатами."""

    def __init__(self, masks: tuple[int, ...] = MASKS):
        """Инициализирует генератор графов.

        Args:
            masks: Кортеж масок соединений

        """
        self.masks = masks
        self.count = len(masks)

    @staticmethod
    def gen_random_graph(masks: tuple[int, ...] = MASKS) -> Graph:
        """Генерирует случайный граф из доступных масок.

        Args:
            masks: Кортеж масок соединений

        Returns:
            Сгенерированный граф

        """
        graph_index = random.randint(0, len(masks) - 1)

        return GraphGenerator.gen_graph(graph_index, masks)

    @staticmethod
    def gen_graph(index: int, masks: tuple[int, ...] = MASKS) -> Graph:
        """Генерирует граф по указанному индексу маски.

        Args:
            index: Индекс маски
            masks: Кортеж масок соединений

        Returns:
            Граф с соединениями из маски

        Raises:
            IndexError: Если индекс вне допустимого диапазона

        """
        if not 0 <= index < len(masks):
            raise IndexError(
                f"Индекс должен быть от 0 до {len(masks) - 1}. Получен: {index}",
            )

        return Graph(masks[index])


def print_graph_info(target_graph: Graph) -> None:
    """Выводит информацию о графе в консоль.

    Args:
        target_graph: Граф для отображения

    """
    connections = target_graph.connections
    if connections is None:
        connections = []

    vertex_connections: dict[int, list[int]] = {i: [] for i in range(9)}

    for a, b in connections:
        vertex_connections[a].append(b)
        vertex_connections[b].append(a)

    print("Граф:")
    print(target_graph)
    print("Связанные комнаты:")

    for room_idx, connected_list in vertex_connections.items():
        if connected_list:
            vertices_list = list(connected_list)
            sorted_vertices = sorted(vertices_list)
            connected_str = ", ".join(str(v) for v in sorted_vertices)
            print(
                f"  Комната {room_idx} соединена с комнатами: {connected_str}",
            )
        else:
            print(f"  Комната {room_idx} не имеет соединений")

    print(f"\nВсего соединений: {len(connections)}")
    print("Список всех связей:")
    for i, (a, b) in enumerate(connections):
        print(f"  Связь {i}: комната {a} <-> комната {b}")


if __name__ == "__main__":
    generator = GraphGenerator(MASKS)

    print(f"Загружено {generator.count} масок.")

    idx_input = input(f"Введите индекс маски (0..{generator.count - 1}): ")
    idx = int(idx_input)

    generated_graph = generator.gen_graph(idx)
    print_graph_info(generated_graph)
