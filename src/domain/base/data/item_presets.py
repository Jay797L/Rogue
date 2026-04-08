import random
from dataclasses import dataclass, field

from domain.base.core.base_item import Item
from domain.base.core.cell import Cell
from domain.base.core.item_category import ItemCategory
from domain.base.data.cell_presets import (
    EatCell,
    ElixirCell,
    KeyCell,
    ScrollCell,
    WeaponCell,
)
from domain.base.data.register_item import (
    register_item_class,
)
from domain.base.utils.point import Point
from domain.game.core.entity_logic.combat import (
    TMTRAINER,
    Attack,
    GradualEffect,
    Heal,
    InstatnceEffect,
    StunEffect,
    TemporaryEffect,
)


@dataclass(eq=False)
class Meat(Item):
    name: str = "Meat"
    specification: str = "Heal 50hp"
    category: ItemCategory = ItemCategory.EAT
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=EatCell)
    strength: int = 50
    attribute: str = "hp"
    action: Heal = field(default_factory=Heal)
    art: tuple[str] = (
        "  ooo   ",
        " o   o  ",
        "o     o ",
        "o  o  o ",
        " o   o  ",
        "  ooo   ",
        "   o    ",
    )


@dataclass(eq=False)
class Fish(Item):
    name: str = "Fish"
    specification: str = "Heal 40hp"
    category: ItemCategory = ItemCategory.EAT
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=EatCell)
    strength: int = 40
    attribute: str = "hp"
    action: Heal = field(default_factory=Heal)
    art: tuple[str] = (
        "   >    ",
        "  / \\   ",
        " <   >  ",
        "  \\ /   ",
        "   ><   ",
        "  /  \\  ",
        "   <>   ",
    )


@dataclass(eq=False)
class Bread(Item):
    name: str = "Bread"
    specification: str = "Heal 30hp"
    category: ItemCategory = ItemCategory.EAT
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=EatCell)
    strength: int = 30
    attribute: str = "hp"
    action: Heal = field(default_factory=Heal)
    art: tuple[str] = (
        "  ###   ",
        " #####  ",
        "####### ",
        " #####  ",
        "  ###   ",
        "  ###   ",
        "   #    ",
    )


@dataclass(eq=False)
class Cheese(Item):
    name: str = "Cheese"
    specification: str = "Heal 20hp"
    category: ItemCategory = ItemCategory.EAT
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=EatCell)
    strength: int = 20
    attribute: str = "hp"
    action: Heal = field(default_factory=Heal)
    art: tuple[str] = (
        "   /\\   ",
        "  /  \\  ",
        " /    \\ ",
        "/______\\",
        " \\    / ",
        "  \\  /  ",
        "   \\/   ",
    )


@dataclass(eq=False)
class Apple(Item):
    name: str = "Apple"
    specification: str = "Heal)"
    category: ItemCategory = ItemCategory.EAT
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=EatCell)
    strength: int = 20
    attribute: str = "hp"
    action: Attack = field(default_factory=Attack)
    art: tuple[str] = (
        "  @@    ",
        " @@@@   ",
        "@@@@@@@ ",
        "@  @  @ ",
        " @@@@   ",
        "  @@    ",
        "   @    ",
    )


@dataclass(eq=False)
class RegenElixir(Item):
    name: str = "Regen Potion"
    specification: str = "Regen 20x20"
    category: ItemCategory = ItemCategory.ELIXIR
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ElixirCell)
    strength: int = 20
    attribute: str = "hp"
    action: GradualEffect = field(default_factory=GradualEffect)
    art: tuple[str] = (
        "  ^^^   ",
        " /   \\  ",
        "|     | ",
        "|  R  | ",
        "|     | ",
        " \\___/  ",
        "  ###   ",
    )


@dataclass(eq=False)
class PoisonElixir(Item):
    name: str = "Poison Potion"
    specification: str = "Poison 20x20"
    category: ItemCategory = ItemCategory.ELIXIR
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ElixirCell)
    strength: int = -10
    attribute: str = "hp"
    action: GradualEffect = field(default_factory=GradualEffect)
    art: tuple[str] = (
        "  ^^^   ",
        " /   \\  ",
        "|     | ",
        "|  P  | ",
        "|     | ",
        " \\___/  ",
        "  XXX   ",
    )


@dataclass(eq=False)
class TemporaryScopeElixir(Item):
    name: str = "Temporary Scope Elixir"
    specification: str = "+10 scope to 20 steps"
    category: ItemCategory = ItemCategory.ELIXIR
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ElixirCell)
    strength: int = 10
    attribute: str = "scope"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    art: tuple[str] = (
        "  ^^^   ",
        " /   \\  ",
        "|     | ",
        "|Scope| ",
        "|     | ",
        " \\___/  ",
        "  ###   ",
    )


@dataclass(eq=False)
class TemporaryStrengthElixir(Item):
    name: str = "Temporary Strength Elixir"
    specification: str = "+30 strength to 20 steps"
    category: ItemCategory = ItemCategory.ELIXIR
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ElixirCell)
    strength: int = 30
    attribute: str = "strength"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    art: tuple[str] = (
        "  ^^^   ",
        " /   \\  ",
        "|     | ",
        "| Str | ",
        "|     | ",
        " \\___/  ",
        "  ###   ",
    )


@dataclass(eq=False)
class TemporaryDexterityElixir(Item):
    name: str = "Temporary Dexterity Elixir"
    specification: str = "+30 dexterity to 20 steps"
    category: ItemCategory = ItemCategory.ELIXIR
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ElixirCell)
    strength: int = 30
    attribute: str = "dexterity"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    art: tuple[str] = (
        "  ^^^   ",
        " /   \\  ",
        "|     | ",
        "| Dex | ",
        "|     | ",
        " \\___/  ",
        "  ###   ",
    )


@dataclass(eq=False)
class ToiletPaper(Item):
    name: str = "Toilet Paper"
    specification: str = "†µ† ®åˆ˜´®"
    category: ItemCategory = ItemCategory.SCROLL
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ScrollCell)
    strength: int = 0
    attribute: str = random.choice(["hp", "max_hp", "dexterity", "strength", "scope"])
    action: TMTRAINER = field(default_factory=TMTRAINER)
    art: tuple[str] = (
        "  ###   ",
        " #   #  ",
        "#  #  # ",
        "#  #  # ",
        "#     # ",
        "  ###   ",
        "   #    ",
    )


@dataclass(eq=False)
class DexterityScroll(Item):
    name: str = "Dexterity Scroll"
    specification: str = "Dexterity up on 5 points"
    category: ItemCategory = ItemCategory.SCROLL
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ScrollCell)
    strength: int = 5
    attribute: str = "dexterity"
    action: InstatnceEffect = field(default_factory=InstatnceEffect)
    art: tuple[str] = (
        " ~~~~~  ",
        "~     ~ ",
        "~ Dex ~ ",
        "~     ~ ",
        "~     ~ ",
        " ~~~~~  ",
        "   #    ",
    )


@dataclass(eq=False)
class StrengthScroll(Item):
    name: str = "Strength Scroll"
    specification: str = "Strength up on 5 points"
    category: ItemCategory = ItemCategory.SCROLL
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ScrollCell)
    strength: int = 5
    attribute: str = "strength"
    action: InstatnceEffect = field(default_factory=InstatnceEffect)
    art: tuple[str] = (
        " ~~~~~  ",
        "~     ~ ",
        "~ Str ~ ",
        "~     ~ ",
        "~     ~ ",
        " ~~~~~  ",
        "   #    ",
    )


@dataclass(eq=False)
class ScopeScroll(Item):
    name: str = "Scope Scroll"
    specification: str = "Scope up on 5 points"
    category: ItemCategory = ItemCategory.SCROLL
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=ScrollCell)
    strength: int = 5
    attribute: str = "scope"
    action: InstatnceEffect = field(default_factory=InstatnceEffect)
    art: tuple[str] = (
        " ~~~~~  ",
        "~     ~ ",
        "~  Sc ~ ",
        "~     ~ ",
        "~     ~ ",
        " ~~~~~  ",
        "   #    ",
    )


@dataclass(eq=False)
class KeyItem(Item):
    name: str = "Key"
    category: ItemCategory = ItemCategory.TREASURE
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=KeyCell)
    strength: int = 0
    attribute: str = ""
    opens_door_id: str = ""
    art: tuple[str] = (
        "  ┌─┐  ",
        "  │ │  ",
        "──┘ └──",
        "  │    ",
        "  └────",
    )


@dataclass(eq=False)
class Sword(Item):
    name: str = "Sword"
    specification: str = "Strength +10"
    category: ItemCategory = ItemCategory.WEAPON
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=WeaponCell)
    strength: int = 10
    attribute: str = "strength"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    dop_attribute: str = "hp"
    dop_strength: int = 0
    dop_effect: None = None
    art: tuple[str] = (
        "  /\\   ",
        " /  \\  ",
        "|    | ",
        "|    | ",
        " \\  /  ",
        "  \\/   ",
        "  ||   ",
    )


@dataclass(eq=False)
class Whip(Item):
    name: str = "Whip"
    specification: str = "Dexterity -10, Stun effect"
    category: ItemCategory = ItemCategory.WEAPON
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=WeaponCell)
    strength: int = -10
    attribute: str = "dexterity"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    dop_attribute: str = "hp"
    dop_strength: int = 0
    dop_effect: StunEffect = field(default_factory=StunEffect)
    art: tuple[str] = (
        "  _    ",
        " / \\   ",
        "|  |   ",
        "|  |   ",
        " \\_/   ",
        "  |    ",
        " / \\   ",
    )


@dataclass(eq=False)
class Staff(Item):
    name: str = "Staff"
    specification: str = "Dexterity +15"
    category: ItemCategory = ItemCategory.WEAPON
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=WeaponCell)
    strength: int = 15
    attribute: str = "dexterity"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    dop_attribute: str = "hp"
    dop_strength: int = 0
    dop_effect: None = None
    art: tuple[str] = (
        "  |    ",
        "  |    ",
        "  |    ",
        " / \\   ",
        "/   \\  ",
        "|   |  ",
        " \\_/   ",
    )


@dataclass(eq=False)
class Dagger(Item):
    name: str = "Dagger"
    specification: str = "Dexterity +10, Poison Effect"
    category: ItemCategory = ItemCategory.WEAPON
    point: Point = Point(0, 0)
    cell: Cell = field(default_factory=WeaponCell)
    strength: int = 10
    attribute: str = "dexterity"
    action: TemporaryEffect = field(default_factory=TemporaryEffect)
    dop_attribute: str = "hp"
    dop_strength: int = -5
    dop_effect: GradualEffect = field(default_factory=GradualEffect)
    art: tuple[str] = (
        "  /\\   ",
        " /  \\  ",
        "|    | ",
        " \\  /  ",
        "  \\/   ",
        "  ||   ",
        "  ||   ",
    )


def register_all_items():
    """Явная регистрация всех предметов из этого модуля."""

    classes = [
        Meat,
        Fish,
        Bread,
        Cheese,
        Apple,
        RegenElixir,
        PoisonElixir,
        TemporaryScopeElixir,
        TemporaryStrengthElixir,
        TemporaryDexterityElixir,
        ToiletPaper,
        DexterityScroll,
        StrengthScroll,
        ScopeScroll,
        KeyItem,
        Sword,
        Whip,
        Staff,
        Dagger,
    ]
    for cls in classes:
        register_item_class(cls)
