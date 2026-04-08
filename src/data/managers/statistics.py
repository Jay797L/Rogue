"""Модуль для работы со статистикой игры."""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from domain.base.data import STRINGS

logger = logging.getLogger(__name__)


@dataclass
class RunStatistics:
    """Статистика одного прохождения."""

    total_treasure: int = 0
    max_level_reached: int = 1
    enemies_killed: int = 0
    food_eaten: int = 0
    elixirs_drank: int = 0
    scrolls_read: int = 0
    weapons_used: int = 0

    hits_dealt: int = 0
    hits_taken: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0

    cells_moved: int = 0
    levels_completed: int = 0

    timestamp: str = field(default_factory=datetime.now().isoformat)
    is_victory: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Преобразует в словарь для JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunStatistics":
        """Создает из словаря."""
        return cls(**data)


@dataclass
class StatisticsManager:
    """Менеджер статистики игры."""

    project_root: Path | None = None

    def __post_init__(self):
        self.stats_file = self.project_root / "data" / "repos" / STRINGS.STATS_FILENAME

        self.stats_file.parent.mkdir(parents=True, exist_ok=True)

        self.current_run: RunStatistics = RunStatistics()

        self.all_runs: list[RunStatistics] = []
        self._load()

    def _load(self):
        """Загружает статистику из файла."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.all_runs = [
                        RunStatistics.from_dict(run) for run in data.get("runs", [])
                    ]
                    logger.info(f"Загружено {len(self.all_runs)} прохождений")
            except Exception as e:
                logger.error(f"Ошибка загрузки статистики: {e}")
                self.all_runs = []

    def save(self):
        """Сохраняет статистику в файл."""
        try:
            data = {
                "runs": [run.to_dict() for run in self.all_runs],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Статистика сохранена в {self.stats_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")

    def add_run(self, run: RunStatistics):
        """Добавляет прохождение."""
        self.all_runs.append(run)
        self.save()

    def get_top_runs(self, limit: int = 10) -> list[RunStatistics]:
        """Возвращает топ прохождений по сокровищам."""
        sorted_runs = sorted(
            self.all_runs,
            key=lambda r: (r.total_treasure, r.max_level_reached),
            reverse=True,
        )
        return sorted_runs[:limit]

    def record_enemy_killed(self):
        """Записывает убийство врага."""
        self.current_run.enemies_killed += 1

    def record_food_eaten(self):
        """Записывает съеденную еду."""
        self.current_run.food_eaten += 1

    def record_elixir_drank(self):
        """Записывает выпитый эликсир."""
        self.current_run.elixirs_drank += 1

    def record_scroll_read(self):
        """Записывает прочитанный свиток."""
        self.current_run.scrolls_read += 1

    def record_weapon_used(self):
        """Записывает смену оружия."""
        self.current_run.weapons_used += 1

    def record_hit_dealt(self, damage: int = 0):
        """Записывает нанесенный удар."""
        self.current_run.hits_dealt += 1
        self.current_run.damage_dealt += damage

    def record_hit_taken(self, damage: int = 0):
        """Записывает полученный удар."""
        self.current_run.hits_taken += 1
        self.current_run.damage_taken += damage

    def record_cell_moved(self):
        """Записывает пройденную клетку."""
        self.current_run.cells_moved += 1

    def record_treasure(self, amount: int):
        """Записывает полученные сокровища."""
        self.current_run.total_treasure += amount

    def record_level_completed(self, level_num: int):
        """Записывает завершение уровня."""
        self.current_run.levels_completed += 1
        self.current_run.max_level_reached = max(
            self.current_run.max_level_reached, level_num
        )

    def record_victory(self):
        """Записывает победу."""
        self.current_run.is_victory = True

    def finish_run(self):
        """Завершает текущее прохождение и сохраняет его."""
        if self.current_run.levels_completed > 0:
            self.add_run(self.current_run)
            logger.info(
                f"Прохождение завершено: уровень {self.current_run.max_level_reached}, "
                f"сокровищ {self.current_run.total_treasure}"
            )
        self.reset_current_run()

    def reset_current_run(self):
        """Сбрасывает текущую сессию."""
        self.current_run = RunStatistics()

    def get_stats_summary(self) -> dict[str, Any]:
        """Возвращает сводку по статистике."""
        if not self.all_runs:
            return {
                "total_runs": 0,
                "best_treasure": 0,
                "best_level": 0,
                "total_enemies": 0,
            }

        return {
            "total_runs": len(self.all_runs),
            "best_treasure": max(r.total_treasure for r in self.all_runs),
            "best_level": max(r.max_level_reached for r in self.all_runs),
            "total_enemies": sum(r.enemies_killed for r in self.all_runs),
        }
