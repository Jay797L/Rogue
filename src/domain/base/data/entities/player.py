from domain.base.backpack import Backpack
from domain.base.core.base_item import Item
from domain.base.core.effect_frame import EffectFrame
from domain.base.data.cell_presets import ExitCell
from domain.base.data.item_presets import KeyItem

from . import _import as ci
from ._export import expose_entity


@ci.dataclass
class PlayerCell(ci.Cell):
    """Клетка игрока."""

    content: str = "@"
    color: ci.COLORS = ci.COLORS.YELLOW


@ci.dataclass(eq=False)
class Player(ci.Character):
    """Игрок."""

    name: str = "player"
    hp: int = 300
    max_hp: int = 300
    strength: int = 70
    dexterity: int = 50
    scope: int = 30
    point: ci.Point = ci.Point(0, 0)
    cell: ci.Cell = ci.field(default_factory=PlayerCell)
    action: ci.Attack = ci.field(default_factory=ci.Attack)
    backpack: Backpack = Backpack()
    equiped_weapon: Item | None = None


def unequip_weapon(player: Player):
    if player.equiped_weapon:
        effect = player.equiped_weapon.action.to_target(player).build()
        effect.frames = [EffectFrame(delay=0, delta=effect.frames[-1].delta)]
        player.equiped_weapon = None
        return effect


def equip_weapon(player: Player, item: Item):
    effect = item.action.to_target(player).build()
    effect.frames.pop()
    player.equiped_weapon = item
    return effect


def player_ai(
    player: Player, direction: ci.Point, map_manager: ci.MapManager
) -> tuple[ci.MoveOrder | None, list[ci.Effect]]:
    target_point = player.point + direction
    target_cell = map_manager[target_point]
    effects = []
    if target_cell is None:
        return ci.MoveOrder(player, target_point), []

    if target_cell.owner:
        if isinstance(target_cell.owner, KeyItem):
            key = target_cell.owner
            if map_manager._game.open_door(key.opens_door_id):
                del map_manager[target_point]
                return ci.MoveOrder(player, target_point), []
        elif isinstance(target_cell.owner, ci.Character):
            difficulty = ci.random.randint(0, 100)
            if difficulty < player.dexterity:
                effects.append(
                    player.action.from_caster(player)
                    .to_target(target_cell.owner)
                    .build()
                )

                if player.equiped_weapon and player.equiped_weapon.dop_effect:
                    effects.append(
                        player.equiped_weapon.dop_effect.from_caster(player)
                        .to_target(target_cell.owner)
                        .by_attribut(player.equiped_weapon.dop_attribute)
                        .by_strength(player.equiped_weapon.dop_strength)
                        .build()
                    )
                return None, effects
        elif isinstance(target_cell.owner, Item):
            discarded_item = player.backpack.add_equipment(target_cell.owner)
            if discarded_item:
                map_manager[player.point] = discarded_item.cell
                discarded_item.point = player.point
                map_manager[target_point] = player.cell
                player.point = target_point
                return None, []
            del map_manager[target_point]
            return ci.MoveOrder(player, target_point), []

        elif isinstance(target_cell, ExitCell):
            del map_manager[target_point]
            return ci.MoveOrder(player, target_point), []

    return None, []


expose_entity(
    module_globals=globals(),
    preset_cls=Player,
    behavior_obj=player_ai,
    register_strategy=ci.CollectionOfBehaviors.register_strategy,
)
