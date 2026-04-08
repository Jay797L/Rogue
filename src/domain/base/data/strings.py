from enum import Enum


class STRINGS(str, Enum):
    NEW_GAME = "New game"
    CONTINUE = "Continue"
    LOAD_GAME = "Load game"
    STATISTICS = "Statistics"
    SETTINGS = "Settings"
    ABOUT = "About"
    MUSIC = "Music"
    EXIT = "Exit"

    MESSAGE_GAME_IS_STARTED = "Game was started!"
    MAIN_MENU_PROMT = "↑/↓ — selection, Enter — confirm, Q — exit"
    PRESS_Q_KEY_TO_RETURN_TO_MENU = "Press Q to return to menu..."

    NO_SAVED_GAMES = "Нет сохранённых игр"
    LOAD_ERROR = "Ошибка загрузки сохранения"
    SAVE_ERROR = "Невозможно сохранить игру (не инициализирован уровень)"
    GAME_SAVED = "Игра сохранена в {}"
    GAME_LOADED = "Игра загружена (уровень {})"
    LOAD_FAILED = "Не удалось загрузить сохранение"
    EXITING_GAME = "Выход из игры..."
    WELCOME_MESSAGE = "Добро пожаловать в игру!"
    SELECT_SAVE_TO_LOAD = "Выберите сохранение для загрузки"

    GAME_OVER = "ВЫ УМЕРЛИ! Игра окончена."
    GAME_OVER_TITLE = "ИГРА ОКОНЧЕНА"
    VICTORY = "ПОБЕДА! Вы прошли все 21 уровень!"
    DOOR_OPENED = "Дверь открыта!"
    LEVEL_UP_MESSAGE = (
        "Уровень {} | Сложность: {}% ↑ | Сила игрока: {}% | Размер карты: {}x"
    )

    MODE_3D_HELP = (
        "3D режим: A/D поворот, W/S вперёд/назад, Q/E стрейф, V переключить на 2D"
    )
    ROTATION_MESSAGE = "Поворот: {}"
    GAME_SAVED_RETURN = "Игра сохранена. Возврат в главное меню"
    RETURN_TO_MENU = "Возврат в главное меню"

    DIRECTION_NORTH = "север"
    DIRECTION_SOUTH = "юг"
    DIRECTION_WEST = "запад"
    DIRECTION_EAST = "восток"

    INVENTORY_TITLE = "INVENTORY"
    INVENTORY_OPEN = "Инвентарь открыт"
    INVENTORY_CLOSED = "Инвентарь закрыт"
    ITEM_USED = "Вы использовали {}: {}"
    SLOT_EMPTY = "Слот {} пуст"
    SLOT_EMPTY_DROP = "Слот {} пуст, нечего выкидывать"
    NO_WEAPON_EQUIPPED = "У вас нет экипированного оружия"
    ITEM_DROPPED = "Вы выкинули {}"
    NO_SPACE_TO_DROP = "Нет свободного места вокруг, некуда выкинуть"
    WEAPON_UNEQUIPPED = "Вы сняли {} (в инвентарь)"
    WEAPON_DROPPED = "Вы сняли {}, он выпал на пол"
    WEAPON_LOST = "Нет места, {} утерян"
    INVENTORY_HELP = (
        "A/S/D/F - select category, 1-9 - select item, Enter - use, I - close"
    )

    CATEGORY_EAT = "EAT"
    CATEGORY_ELIXIR = "ELIXIR"
    CATEGORY_SCROLL = "SCROLL"
    CATEGORY_WEAPON = "WEAPON"

    STATS_TITLE = "=== STATISTICS (TOP 10) ==="
    STATS_NO_DATA = "No statistics yet. Play the game!"
    STATS_SUMMARY = "Total runs: {} | Best treasure: {} | Best level: {}"
    STATS_VICTORY_MARK = "✓"
    STATS_HEADER_NUM = "#"
    STATS_HEADER_TREASURE = "Treasure"
    STATS_HEADER_LEVEL = "Level"
    STATS_HEADER_KILLS = "Kills"
    STATS_HEADER_FOOD = "Food"
    STATS_HEADER_ELIXIR = "Elixir"
    STATS_HEADER_SCROLLS = "Scrolls"
    STATS_HEADER_VICTORY = "Victory"

    MAP_TITLE = " MAP "
    MESSAGES_TITLE = " MESSAGES "
    SAVE_HINT = " S - сохранить "
    TREASURE_LABEL = "TREASURE: {:05d}"

    HELP_LOAD_GAME = "↑/↓ - select, Enter - load, Q - back to menu"
    HELP_GAME_OVER = "Press Q to return to menu..."

    ENEMY_ZOMBIE = "zombie"
    ENEMY_GHOST = "ghost"
    ENEMY_OGR = "ogr"
    ENEMY_SNAKE_MAGE = "snake_mage"
    ENEMY_VAMPIRE = "vampire"
    ENEMY_MIMIK = "mimik"

    ELITE_PREFIX = "Elite"
    BOSS_PREFIX = "Boss"
    ENEMY_TYPE_ENEMY = "Enemy"
    TREASURE_REWARD = "+{}💰 за убийство {} {}!"

    STATUS_FORMAT = "HP: {}/{}, STR: {}, DEX: {}, SCP: {}, LVL: {}"

    AUTO_SAVE_FILENAME = "auto_save.json"
    SAVE_FILENAME_PATTERN = "save_{}.json"
    STATS_FILENAME = "statistics.json"

    MENU_SELECTION_FORMAT = "> {} <"
