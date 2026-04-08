from dataclasses import dataclass


@dataclass
class Pixel:
    """Пиксель для отображения на клиенте."""

    y: int
    x: int
    content: str
    color: int
