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
        player_start_point=None,
    ):
        import logging

        logger = logging.getLogger(__name__)

        if seed is not None:
            self.current_seed = seed
        else:
            self.current_seed = int(time.time())

        logger.info(
            f"=== INITIALIZING LEVEL: difficulty={difficulty}, seed={self.current_seed} ==="
        )

        self.level = LevelGenerator.level_gen(
            player=self.player,
            difficulty=difficulty,
            seed=self.current_seed,
            opened_doors=opened_doors or self.opened_doors,
            player_start_point=player_start_point,
        )

        if self.level is None:
            logger.error("LevelGenerator.level_gen returned None")
            raise RuntimeError("Failed to generate level")

        if not hasattr(self.level, "map_manager") or not self.level.map_manager:
            logger.error("Level has no map_manager")
            raise RuntimeError("Level has no map_manager")

        logger.info(
            f"Level created successfully. Map cells: {len(self.level.map_manager._content)}"
        )

        self.level.map_manager._game = self

        # Set game reference for all entities' actions to record hit statistics
        game_ref = self
        for point, cell in self.level.map_manager._content.items():
            owner = getattr(cell, "owner", None)
            if (
                owner is not None
                and hasattr(owner, "action")
                and owner.action is not None
            ):
                if hasattr(owner.action, "game"):
                    owner.action.game = game_ref
        if (
            hasattr(self.player, "action")
            and self.player.action is not None
            and hasattr(self.player.action, "game")
        ):
            self.player.action.game = game_ref

        self._setup_vision()
        logger.info("=== LEVEL INITIALIZATION COMPLETE ===")
