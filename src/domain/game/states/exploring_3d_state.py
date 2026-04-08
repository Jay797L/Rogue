"""Состояние исследования в 3D-режиме с поворотом на 90° и клеточным движением."""

from domain.base.data.strings import STRINGS
from domain.base.utils.directions import DOWN, LEFT, RIGHT, UP
from domain.base.utils.point import Point
from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState

from .base_state import GameStateBase


class Exploring3DState(GameStateBase):
    """
    3D-режим: A/D поворот на 90°, W/S вперёд/назад, Q/E стрейф влево/вправо.
    Движение по клеткам, без плавности.
    """

    DIR_VECTORS = [
        RIGHT,
        DOWN,
        LEFT,
        UP,
    ]

    def handle_input(self, action: GameKey) -> bool:
        if action == GameKey.KEY_A:
            self.game.player_direction = (self.game.player_direction - 1) % 4
            self._refresh_vision()

            return True
        elif action == GameKey.KEY_D:
            self.game.player_direction = (self.game.player_direction + 1) % 4
            self._refresh_vision()

            return True
        elif action == GameKey.KEY_W:
            self._move_relative(forward=True, sideways=False)
            return True
        elif action == GameKey.KEY_S:
            self._move_relative(forward=False, sideways=False)
            return True
        elif action == GameKey.KEY_Q:
            self.game.save_game(is_auto=True)
            self.game.message = STRINGS.GAME_SAVED_RETURN
            self.game.fsm.transition_to(GameState.MENU)
            return True
        elif action == GameKey.KEY_V:
            self.game.switch_vision_mode(False)
            self.game.fsm.transition_to(GameState.EXPLORING)
            return True
        elif action == GameKey.INVENTORY:
            return self.game.handle_inventory_open(action)
        elif action == GameKey.SAVE_GAME:
            return self.game.save_game()
        return True

    def _refresh_vision(self):
        """Обновляет угол обзора в vision_instance."""
        if hasattr(self.game._vision_instance, "set_direction"):
            self.game._vision_instance.set_direction(self.game.player_direction)

    def _move_relative(self, forward: bool, sideways: bool, left: bool = True):
        """
        Выполняет движение относительно текущего направления игрока.
        forward=True -> движение вперёд, forward=False -> назад.
        sideways=True -> движение влево (left=True) или вправо (left=False).
        """
        dir_idx = self.game.player_direction
        if forward:
            direction = self.DIR_VECTORS[dir_idx]
        elif sideways:
            if left:
                direction = self.DIR_VECTORS[(dir_idx - 1) % 4]
            else:
                direction = self.DIR_VECTORS[(dir_idx + 1) % 4]
        else:
            direction = self.DIR_VECTORS[(dir_idx + 2) % 4]

        self._try_move(direction)

    def _try_move(self, direction: Point):
        """Пытается переместить игрока в заданном направлении через штатную логику player_ai."""
        behavior = self.game.level.enemy_manager.behavior_enforcer
        effects = behavior.perform_player_behavior(direction)

        self._refresh_vision()

        for effect in effects:
            self.game.level.enemy_manager.active_effects.append(effect)

        self.game.level.enemy_manager.update()
        self.game.level.enemy_manager.effects_apply()

        if self.game.player.point == self.game.level.exit_point:
            self.game.next_level()

            self._refresh_vision()

        if self.game.player.hp <= 0:
            self.game.game_over()

    def _dir_name(self) -> str:
        names = [
            STRINGS.DIRECTION_EAST.value,
            STRINGS.DIRECTION_SOUTH.value,
            STRINGS.DIRECTION_WEST.value,
            STRINGS.DIRECTION_NORTH.value,
        ]
        return names[self.game.player_direction % 4]

    def on_enter(self):
        """При входе в 3D режим."""
        if not self.game.is_3d_mode:
            self.game.switch_vision_mode(True)
        self.game.message = STRINGS.MODE_3D_HELP
        self.game._setup_vision()
        self._refresh_vision()

    def on_exit(self):
        pass

    def update(self) -> bool:
        if self.game.player.hp <= 0:
            self.game.game_over()
        return True
