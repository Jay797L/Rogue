"""Модуль для рендеринга ASCII-арта в 3D с правильным масштабированием."""


class ASCIIArtRenderer:
    """Рендерер ASCII-арта с поддержкой масштабирования."""

    @classmethod
    def get_art(cls, entity, max_height: int = 5, max_width: int = 5) -> list[str]:
        """
        Возвращает ASCII-арт для сущности с учетом максимальных размеров.

        Args:
            entity: Сущность (игрок, враг, предмет)
            max_height: Максимальная высота арта в строках
            max_width: Максимальная ширина арта в символах

        Returns:
            Список строк с ASCII-артом
        """

        original_art = cls._get_original_art(entity)
        if not original_art:
            return ["?"]

        return cls._scale_art(original_art, max_height, max_width)

    @classmethod
    def _get_original_art(cls, entity) -> list[str] | None:
        """Получает оригинальный арт сущности."""
        if hasattr(entity, "art") and entity.art:
            return list(entity.art)
        return None

    @classmethod
    def _scale_art(cls, art: list[str], max_height: int, max_width: int) -> list[str]:
        """
        Масштабирует ASCII-арт до указанных максимальных размеров.
        Сохраняет пропорции и не дублирует символы.
        """
        if not art:
            return []

        original_height = len(art)
        original_width = max(len(line) for line in art)

        height_scale = max_height / original_height
        width_scale = max_width / original_width
        scale = min(height_scale, width_scale, 2.0)

        if scale <= 1.0:
            return cls._crop_art(art, max_height, max_width)

        scaled_height = int(original_height * scale)
        scaled_width = int(original_width * scale)

        scaled_art = []
        for i in range(scaled_height):
            src_row = int(i / scale)
            if src_row >= original_height:
                src_row = original_height - 1

            original_line = art[src_row]

            scaled_line = []
            for j in range(scaled_width):
                src_col = int(j / scale)
                if src_col >= len(original_line):
                    src_col = len(original_line) - 1
                scaled_line.append(original_line[src_col])

            scaled_art.append("".join(scaled_line))

        return scaled_art

    @staticmethod
    def _crop_art(art: list[str], max_height: int, max_width: int) -> list[str]:
        """Обрезает арт до указанных размеров."""
        if len(art) > max_height:
            start = (len(art) - max_height) // 2
            art = art[start : start + max_height]
        result = []
        for line in art:
            if len(line) > max_width:
                start = (len(line) - max_width) // 2
                line = line[start : start + max_width]
            result.append(line)
        return result
