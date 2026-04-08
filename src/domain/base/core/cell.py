from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from domain.base.data import COLORS


@dataclass
class Cell:
    content: str = " "
    blocking_vision: bool = False
    viewed: bool = False
    memorable: bool = False
    owner: Optional["Character"] = None
    color: "COLORS" = field(init=False)

    def __post_init__(self):

        from domain.base.data import COLORS

        if not hasattr(self, "color"):
            self.color = COLORS.WHITE
