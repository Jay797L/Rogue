"""Инфраструктурные модули."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

DISABLE_LOGERS = []


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
    enable_console: bool = False,
    log_dir: Path | None = None,
    project_root: Path | None = None,
    disabled_loggers: list[str] | None = None,
    enable_error_log: bool = False,
    enable_debug_log: bool = False,
) -> logging.RootLogger:
    """Настройка логирования с разными обработчиками

    Args:
        level: Уровень логирования
        log_file: Конкретный файл для логов (если указан)
        enable_console: Включить вывод в консоль
        log_dir: Директория для логов (если не указана, используется project_root / "logs")
        project_root: Корневая директория проекта (где находится main.py)
        disabled_loggers: Список логгеров для отключения
    """

    if log_dir is None:
        log_dir = project_root / "src"/ "data" / "repos" /"logs" if project_root is not None else Path("logs")

    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    root_logger.setLevel(level)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
            )
        )
        root_logger.addHandler(console_handler)

    if log_file:
        all_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        all_handler.setLevel(level)
        all_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(all_handler)
    else:
        game_log = log_dir / "game.log"
        all_handler = RotatingFileHandler(
            game_log,
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        all_handler.setLevel(level)
        all_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(all_handler)

    if enable_error_log:
        error_handler = RotatingFileHandler(
            log_dir / "errors.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(error_handler)

    if enable_debug_log and level <= logging.DEBUG:
        debug_handler = RotatingFileHandler(
            log_dir / "debug.log", maxBytes=20_000_000, backupCount=2, encoding="utf-8"
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s.%(msecs)03d - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root_logger.addHandler(debug_handler)

    if disabled_loggers:
        for name in disabled_loggers:
            lg = logging.getLogger(name)
            lg.disabled = True

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер для указанного модуля."""
    return logging.getLogger(name)


__all__ = ["DISABLE_LOGERS", "setup_logging", "get_logger"]
