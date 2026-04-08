import logging
import sys
import traceback
from pathlib import Path

from domain.base.difficulty_config import (
    difficulty_config,
)
from domain.game.core.game import Game
from domain.vision.vision_fog_of_war import FogOfWarVision
from domain.vision.vision_pseudo3d import Pseudo3DVision
from domain.vision.vision_unlimited import UnlimitVision
from infrastructure.log import DISABLE_LOGERS, get_logger, setup_logging
from infrastructure.music import MusicPlayer
from presentation.game_view import CursesGameView


def main():
    try:
        project_root = Path(__file__).resolve().parent

        repos = project_root / "data" / "repos"
        (repos / "saves").mkdir(parents=True, exist_ok=True)
        (repos / "logs").mkdir(parents=True, exist_ok=True)
        (repos / "debug_snapshots").mkdir(parents=True, exist_ok=True)
        (repos / "configs").mkdir(parents=True, exist_ok=True)

        log_level = logging.INFO
        if "--debug" in sys.argv:
            log_level = logging.DEBUG
        elif "--verbose" in sys.argv:
            log_level = logging.INFO
        elif "--quiet" in sys.argv:
            log_level = logging.ERROR

        enable_file_logging = "--log" in sys.argv or log_level != logging.INFO
        if enable_file_logging:
            log_file = repos / "logs" / "game.log"
            setup_logging(
                level=log_level,
                log_file=log_file,
                enable_console=False,
                log_dir=repos / "logs",
                project_root=project_root,
                disabled_loggers=DISABLE_LOGERS,
                enable_error_log=True,
                enable_debug_log=(log_level <= logging.DEBUG),
            )
        else:
            logging.basicConfig(
                handlers=[logging.NullHandler()], level=logging.CRITICAL
            )

        logger = get_logger(__name__)

        if enable_file_logging:
            logger.info("=" * 50)
            logger.info(f"Project root: {project_root}")
            logger.info(
                f"Game starting with log level: {logging.getLevelName(log_level)}"
            )
            logger.info(f"Log file: {log_file.absolute()}")
            logger.info("=" * 50)

        config_path = repos / "configs" / "difficulty.json"
        if config_path.exists():
            difficulty_config.load_from_file(config_path)
            if enable_file_logging:
                logger.info(f"Loaded difficulty config from {config_path}")
        else:
            difficulty_config.save_to_file(config_path)
            if enable_file_logging:
                logger.info(f"Created default difficulty config at {config_path}")

        if "--all" in sys.argv:
            vision_class = UnlimitVision
        elif "--3d" in sys.argv:
            vision_class = Pseudo3DVision
        else:
            vision_class = FogOfWarVision

        if enable_file_logging:
            logger.info(f"Vision mode: {vision_class.__name__}")

        music_path = project_root / "data" / "repos" / "music.mp3"
        music_player = MusicPlayer(music_path)
        music_player.play()
        if enable_file_logging:
            logger.info("Background music started")

        game = Game(vision_class=vision_class, project_root=project_root)
        game.set_music_player(music_player)
        settings_manager = game.settings_manager
        if settings_manager and music_player:
            if settings_manager.get_music_enabled():
                music_player.unpause()
            else:
                music_player.pause()
        view = CursesGameView(game)
        view.run()

        logger.info("Game finished normally")

    except Exception as e:
        try:
            logger = get_logger(__name__)
            logger.exception("Fatal error occurred")
        except:
            print(f"FATAL ERROR: {e}")

            traceback.print_exc()


if __name__ == "__main__":
    main()
