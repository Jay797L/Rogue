#!/usr/bin/env python3
import curses


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Список клавиш для проверки (латиница и ожидаемая русская)
    test_keys = [
        ("w", "ц"),
        ("s", "ы"),
        ("a", "ф"),
        ("d", "в"),
        ("k", "к"),
        ("j", "о"),
        ("h", "р"),
        ("l", "д"),
        ("i", "ш"),
        ("q", "й"),
        ("v", "м"),
        ("e", "у"),
        ("r", "к"),
        ("g", "п"),
        ("z", "я"),
        ("x", "ч"),
        ("f", "а"),
        ("t", "е"),
        ("y", "н"),
        ("u", "г"),
        ("c", "с"),
        ("b", "и"),
        ("n", "т"),
        ("m", "ь"),
    ]

    results = []

    stdscr.addstr(
        0, 0, "Тест клавиш с get_wch() (русская раскладка должна быть включена)"
    )
    stdscr.addstr(
        1, 0, "Для каждой латинской буквы нажмите соответствующую русскую клавишу."
    )
    stdscr.addstr(2, 0, "Нажмите любую клавишу для продолжения...")
    stdscr.getch()

    for latin, russian in test_keys:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Латинская '{latin}' -> ожидаемая русская '{russian}'")
        stdscr.addstr(1, 0, "Нажмите нужную клавишу...")
        try:
            key = stdscr.get_wch()
        except Exception as e:
            key = f"ERROR: {e}"
        results.append((latin, russian, key))
        # Показываем код символа для отладки
        if isinstance(key, str) and len(key) > 0:
            code_info = f" (unicode: {ord(key)})"
        else:
            code_info = ""
        stdscr.addstr(3, 0, f"Получено: '{key}'{code_info} (тип {type(key).__name__})")
        stdscr.addstr(4, 0, "Нажмите любую клавишу для следующей...")
        stdscr.getch()

    # Вывод результатов
    stdscr.clear()
    stdscr.addstr(0, 0, "РЕЗУЛЬТАТЫ ТЕСТА (get_wch):")
    row = 2
    for latin, russian, got in results:
        line = f"Лат '{latin}' (рус '{russian}') -> получено '{got}'"
        if row < height - 1:
            stdscr.addstr(row, 0, line[: width - 1])
        row += 1
    stdscr.addstr(row + 1, 0, "Нажмите любую клавишу для выхода...")
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
