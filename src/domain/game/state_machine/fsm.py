from domain.game.state_machine.game_key import GameKey
from domain.game.state_machine.game_state import GameState
from domain.game.states import (
    AboutState,
    Exploring3DState,
    ExploringState,
    GameOverState,
    GameStateBase,
    InventoryState,
    LoadGameState,
    MenuState,
    SettingsState,
)


class FiniteStateMachine:
    """
    Finite State Machine that manages game states.
    """

    def __init__(self, game):
        self.game = game
        self.states: dict[GameState, GameStateBase] = {
            GameState.MENU: MenuState(game),
            GameState.EXPLORING: ExploringState(game),
            GameState.INVENTORY: InventoryState(game),
            GameState.GAME_OVER: GameOverState(game),
            GameState.EXPLORING_3D: Exploring3DState(game),
            GameState.LOAD_GAME: LoadGameState(game),
            GameState.SETTINGS: SettingsState(game),
            GameState.ABOUT: AboutState(game),
        }
        self.current_state: GameState = GameState.MENU
        self.current_state_instance: GameStateBase = self.states[GameState.MENU]
        self._previous_state = None

        self.current_state_instance.on_enter()

    def process_action(self, action: GameKey) -> bool:
        """Process an action based on current state."""
        result = self.current_state_instance.handle_input(action)
        return result if result is not None else True

    def transition_to(self, new_state: GameState, **kwargs):
        """Transition to a new state."""
        if new_state == self.current_state:
            return

        self.current_state_instance.on_exit()

        self._previous_state = self.current_state
        self.current_state = new_state
        self.current_state_instance = self.states[new_state]

        if kwargs and hasattr(self.current_state_instance, "on_enter"):
            self.current_state_instance.on_enter(**kwargs)
        else:
            self.current_state_instance.on_enter()

    def update(self) -> bool:
        """Update current state logic."""
        return self.current_state_instance.update()

    def get_current_state(self) -> GameState:
        """Get the current game state."""
        return self.current_state
