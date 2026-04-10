#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ ":$PATH:" != *":$SCRIPT_DIR:"* ]] && export PATH="$PATH:$SCRIPT_DIR"
[ -f "$SCRIPT_DIR/.venv/bin/activate" ] && source "$SCRIPT_DIR/.venv/bin/activate"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Проверяем, есть ли аргументы командной строки
if [ $# -eq 0 ]; then
    echo "Ничего не пришло, скрипт завершается"
    exit 0
else
    echo "Получены аргументы, запускаем Python в цикле с задержкой 1 секунда"
    while true; do
        # ./lint.sh
        python3 "$@"
        sleep 0.1
    done
fi