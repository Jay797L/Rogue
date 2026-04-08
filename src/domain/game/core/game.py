import time
from pathlib import Path

from domain.base.core.base_game import BaseGame
from domain.map.level_generation.level_generator import LevelGenerator
from infrastructure.log import get_logger

logger = get_logger(__name__)


class Game(BaseGame):
    """Основной игровой режим с генерацией карты через LevelGenerator."""

    def __init__(self, vision_class=None, project_root: Path | None = None):
        super().__init__(vision_class, project_root)
        self.current_seed = int(time.time())
        self._3d_vision_instance = None
        self._2d_vision_instance = None

    def _initialize_level(
        self,
        difficulty: int = 1,
        seed: int | None = None,
        opened_doors: list[str] | None = None,
    ):
        if seed is not None:
            self.current_seed = seed
        else:
            self.current_seed = int(time.time())

        self.level = LevelGenerator.level_gen(
            player=self.player,
            difficulty=difficulty,
            seed=self.current_seed,
            opened_doors=opened_doors or self.opened_doors,
        )

        if self.level is None:
            raise RuntimeError("Failed to generate level")

        if not hasattr(self.level, "map_manager") or not self.level.map_manager:
            raise RuntimeError("Level has no map_manager")
        self.level.map_manager._game = self

        self._setup_vision()
