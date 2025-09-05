# Project Team 01 — Python_Bootcamp

**Summary:** In this team project, you'll develop a console-based roguelike game application in the Python programming language using the curses library, inspired by the classic 1980 game Rogue.

💡 [Click here](https://new.oprosso.net/p/4cb31ec3f47a4596bc758ea1861fb624) to give us feedback on this project. It’s anonymous and helps us improve the course. We recommend filling out the survey right after completing the project.

## Table of Contents

  - [Chapter I](#chapter-i)
    - [Instructions](#instructions)
  - [Chapter II](#chapter-ii)
    - [General Information](#general-information)
      - [Rogue 1980](#rogue-1980)
      - [Application Architecture](#application-architecture)
  - [Chapter III](#chapter-iii)
    - [Task 0 — How Did We Get Here?](#task-0--how-did-we-get-here)
    - [Task 1 — The Essential Essences of the Game](#task-1--the-essential-essences-of-the-game)
    - [Task 2 — Energetic Gameplay](#task-2--energetic-gameplay)
    - [Task 3 — Procedural World](#task-3--procedural-world)
    - [Task 4 — Cozy 2D](#task-4--cozy-2d)
    - [Task 5 — Cartridge With a Battery](#task-5--cartridge-with-a-battery)
    - [Bonus Task 6 — You Shall Not Pass!](#bonus-task-6--you-shall-not-pass)
    - [Bonus Task 7 — The Art of Balance](#bonus-task-7--the-art-of-balance)
    - [Bonus Task 8 — Imagine You’re a Table](#bonus-task-8--imagine-youre-a-table)
    - [Bonus Task 9 — Full 3D](#bonus-task-9--full-3d)


## Chapter I 
### Instructions

1. Throughout the course, you will often feel uncertain and have limited information, but that's all part of the experience. Remember, the repository and Google are always there for you. So are your peers and Rocket.Chat. Talk. Search. Use your common sense. Don't be afraid to make mistakes.
2. Be mindful of your sources. Cross-check. Think critically. Analyze. Compare.
3. Read the tasks carefully, and then read them again.
4. Pay close attention to the examples, too. They may include information that is not explicitly stated in the task itself.
5. You may encounter inconsistencies when something in the task or example contradicts what you thought you knew. Try to figure them out. If you can't, write it down as an open question and resolve it as you go. Don't leave questions unresolved.
6. If a task seems unclear or impossible, it probably just feels that way. Break it down into parts. Most of them will make sense on their own.
7. You’ll encounter all kinds of tasks. The bonus ones are for those who are curious and detail-oriented. They’re optional and more challenging, but completing them gives you extra experience and insight.
8. Don't try to cheat the system or your peers. Ultimately, you'll only be cheating yourself.
9. Got a question? Ask the peer to your right. If that doesn't help, ask the peer to your left.
10. When asking for help, always make sure you understand the why, how, and what-for. Otherwise, the help won't be very useful.
11. Always push your code to the develop branch only. The master branch will be ignored. Work inside the src directory.
12. Your directory should not contain any files besides those required for the tasks.

## Chapter II 
### General Information

#### Rogue 1980

![RogueMap](misc/images/rogue-map-2.png)

![Dungeon](misc/images/dungeon.png)

Rogue, short for "rogue" or "scoundrel," is a computer game developed by Epyx in 1980. Its core theme is dungeon exploration. Rogue was hugely popular on university Unix systems in the early 1980s and gave birth to an entire genre of games known as roguelikes.

In Rogue, players take on the classic fantasy role of an adventurer. The game begins on the uppermost level of an unmapped dungeon filled with monsters and treasures. As players progress deeper into the randomly generated dungeon, the enemies grow stronger and the challenges intensify.

Each dungeon level consists of a 3×3 grid of rooms or dead-end corridors that would have otherwise led to a room. Later versions of the game added "mazes" — winding corridors filled with dead ends — alongside traditional rooms. Unlike most adventure games of that era, Rogue uses procedural generation to create unique and equally risky dungeon layouts and item placements for both newcomers and seasoned players.

The player has three main attributes: health, strength, and experience. All three can be increased by using potions or scrolls and decreased by stepping on traps or reading cursed scrolls. The wide variety of magical potions, scrolls, wands, weapons, armor, and food results in rich, diverse gameplay with many different paths to victory or defeat.

#### Application Architecture

When developing projects involving data, business logic, and user interfaces, a multi-layered architecture is commonly used. A typical structure includes the following layers:

- Presentation Layer (View, UI);
- Domain Layer (Business Logic);
- Data Layer (Data Access, Data Source).

Separating business logic from presentation logic makes structuring your application easier and decoupling components with different levels of stability simpler.

The **presentation layer** should contain the code responsible for displaying content on the user’s screen and handling user input. In this project, this includes interactions between the curses library and the domain layer.

The **domain layer** defines the core game logic, independent of any frameworks. It includes the main entities of the game, such as the game itself, the player, enemies, levels, and the map. For instance, the player's position and the logic for updating numeric attributes on the map reside in this layer and are then passed to the presentation layer for rendering.

Following the principles of **clean architecture**, note that the domain layer must not depend on any other layers. This is achieved using the **dependency inversion principle**.

To organize communication between layers more effectively, you may also adopt one of the **MVC family patterns** (such as MVP, MVVM, or MVPVM). These approaches connect the logic layer (Model) and the presentation layer (View) through intermediary service layers (Controller, Presenter, ViewModel, etc.). Different languages and frameworks may favor different implementations, but the underlying principles remain similar.

In this project, the **data layer** is responsible for managing data, including saving the history of previous runs and the state of the current game session.

## Chapter III

## Task 0 — How Did We Get Here?

The game application must:

- Be implemented in **Python 3.10**.
- Use a **console interface** based on the curses library.
- Be fully **keyboard-controlled**.
- Have a well-structured, clean architecture with clearly separated layers.
- Implement the core mechanics of the classic Rogue (1980) game with some simplifications (specific gameplay requirements are described in the following tasks).
- Where the gameplay design is not explicitly defined in this document, refer to the logic of the original 1980 version as a valid fallback.

## Task 1 — The Essential Essences of the Game

The game must adhere to the layer separation outlined in the Application Architecture section. Clearly separate the domain and gameplay layers, the rendering layer, and the data layer.

To start development, implement the **domain layer**, which defines the game’s core entities. The list below includes the recommended entities and their **basic attributes** (this is a required but non-exhaustive list):

- Game session.
- Level.
- Room.
- Corridor.
- Character, with:
  + maximum health,
  + current health,
  + dexterity,
  + strength,
  + current weapon.
- Backpack.
- Enemy, with:
  + type,
  + health,
  + dexterity,
  + strength,
  + hostility.
- Item, with:
  + type,
  + subtype,
  + health (number of health points restored, for food),
  + maximum health (points increased by scrolls or elixirs — also increases current max health),
  + dexterity (points increased by scrolls or elixirs),
  + strength (points increased by scrolls, elixirs, or weapons),
  + value (for treasure).

## Task 2 — Energetic Gameplay

Implement the game’s core mechanics within the **domain layer**, keeping them independent of the presentation and data layers.

### Gameplay Logic

- The game must include 21 dungeon levels.
- Each level should consist of 9 rooms connected by corridors — every room must be accessible from any other via these corridors.
- Each room may contain enemies and items, except for the starting room.
- The player controls the character's movement, can interact with items, and fight enemies.
- The goal is to find the exit to the next level on each floor and advance through all 21 levels.
- On each level, the player starts in a random position within the starting room, which is guaranteed to be free of enemies.
- If the main character dies, the game state is **reset**, and everything starts from the beginning.
- With each new level: the enemy quantity and difficulty increase, the availability of useful items decreases, the amount of treasure dropped by defeated enemies increases.
- After every run, whether completed or not, the player’s result is saved in a high score table, which includes the deepest level reached and the amount of treasure collected. The table must be sorted by the amount of treasure collected.
- The entire game must be **turn-based**; each player action triggers enemy actions. Until the player makes a move, the game world remains idle.

### Character Logic

- The health attribute reflects the character’s current health. If health drops to 0 or below, the game ends.
- The maximum health attribute defines the character’s health cap, which can be restored by consuming food.
- The dexterity attribute affects the hit chance formula for both enemies attacking the character and the character attacking enemies.
- The strength attribute determines the base damage dealt by the character when unarmed and is also a factor in damage calculations with weapons.
- Upon defeating an enemy, the character receives a number of treasure points, depending on the enemy’s difficulty.
- The character can pick up items and store them in a backpack, then use them later.
- Each item can modify the character’s attributes, either temporarily or permanently, when used.
- When the character reaches a level’s exit, they are automatically moved to the next level.

### Enemy Logic

- Each enemy has attributes similar to the player’s: health, dexterity, and strength. In addition, each enemy has a hostility attribute.
- The hostility value determines the distance at which the enemy starts chasing the player.

#### There are 5 enemy types:

- **Zombie** (displayed as green z): low dexterity, medium strength and hostility, and high health.
- **Vampire** (displayed as red v): high dexterity, hostility, and health; medium strength. Steals some of the player's maximum health on a successful attack. The first attack against a vampire always misses.
- **Ghost** (displayed as white g): high dexterity, low strength, hostility, and health. It constantly teleports within the room and periodically becomes invisible until combat begins.
- **Ogre** (displayed as yellow o): moves two tiles per turn within the room. Very high strength and health. Rests for one turn after every attack, then guaranteed counterattack. Low dexterity, medium hostility.
- **Snake Mage** (displayed as white s): very high dexterity. Moves diagonally and constantly switches direction. Each successful attack has a chance to put the player to sleep for one turn. High hostility.
- Each enemy type has its own movement pattern within rooms.
- Once an enemy starts chasing the player, all monsters behave the same: they move toward the player along the shortest path using adjacent tiles.
- If the player enters a monster’s aggression range but there is no valid path to the player, the monster continues moving randomly according to its own pattern.

### Environment Logic

- Each item type has a specific function:
  - **Treasure** has a value, accumulates, and affects the final score. It can only be obtained by defeating enemies.
  - **Food**: restores health by a certain amount.
  - **Elixirs**: temporarily increase one attribute (dexterity, strength, or max health).
  - **Scrolls**: permanently increase one attribute (dexterity, strength, or max health).
  - **Weapons** have a strength attribute and modify the damage formula when used.
- When maximum health increases, current health also increases by the same amount.
- If an elixir effect ends and the player's health drops to 0 or below, the health must be reset to the minimum possible positive value to allow the game to continue.
- The backpack stores all item types.
- When the character steps on an item, it is automatically added to the backpack if there’s room (up to 9 items per type; treasure stacks in a single slot).
- Food, elixirs, and scrolls are consumed on use.
- Weapons, when unequipped, are dropped onto a neighboring tile.

#### Dungeon Level Structure:

- The deeper the level, the more difficult it becomes.
- Each level consists of rooms connected by corridors.
- Rooms contain enemies and items.
- Both enemies and the player can move between rooms and corridors.
- Each level has a guaranteed exit to the next level.
- Reaching the exit of the final level ends the game.

### Combat Logic

- Combat is resolved in a **turn-based** manner.
- An attack is triggered when the player moves toward an enemy.
- Combat is initiated upon contact with an enemy.
- Attacks are resolved step-by-step in turns:
    1. **Hit check**: determines whether the attack lands. The result is random and depends on the attacker’s and target’s dexterity.
    2. **Damage calculation**: based on the attacker’s strength and weapon modifiers (if applicable).
    3. **Apply damage**: subtract the damage from the target’s health. If the target's health drops to 0 or below, they die.
- Upon defeating an enemy, the player receives a random amount of treasure based on the enemy’s hostility, strength, dexterity, and health.

## Task 3 — Procedural World

Implement a level generation module within the **domain layer**.

- Each level should be logically divided into 9 sections. Within each section, a room is generated randomly with an arbitrary size and position.
- Rooms are connected by randomly generated corridors. The corridors have their own geometry and are walkable, meaning their coordinates must be generated and stored. The generator must ensure that the resulting graph of rooms is connected and contains no errors.
- Each level must include one starting room (where the game session begins) and one exit room, which contains a portal or tile that moves the player to the next level upon contact.
- An example implementation of level generation can be found in the code samples folder.

## Task 4 — Cozy 2D

Implement game rendering using the curses library within the **presentation layer**, leveraging the necessary domain entities.

### Rendering Requirements

- Environment rendering: display walls, floors, doorways, and corridors connecting rooms.
- Actor rendering: display the player, enemies, and collectible items.
- UI rendering: display the game interface, including a status panel, inventory, and a simple menu.

### Fog of War Logic

The rendering behavior depends on the player's state and visibility:

- Unexplored rooms and corridors are not rendered.
- Discovered but unoccupied rooms appear only as walls.
- The room currently occupied by the player displays walls, floors, actors, and items.
- When the player is near a room but still in a corridor, only the line-of-sight area is revealed using **ray casting** and the **Bresenham algorithm** for visibility determination.

An example implementation of level rendering is available in the code-samples folder.

### Controls

**Player Movement and Actions:**

- Move using the WASD keys.
- Use a weapon from the backpack — press H.
- Use food — press J.
- Use an elixir — press K.
- Use a scroll — press E.

**Item Selection:**

- Using any item from the backpack should display a list of items of that type on the screen and prompt the player to select one (slots 1–9).
- When selecting a weapon, the player should also have the option to unequip the current weapon without dropping it. Therefore, weapon selection must allow choices from 0 to 9, where 0 means "empty hands".

### Statistics

The game collects and displays statistics in a separate view, showing data from all playthroughs sorted by total treasure collected.  

The following data points should be tracked:
- Amount of treasure collected;
- Level reached;
- Number of enemies defeated;
- Amount of food consumed;
- Number of elixirs used;
- Number of scrolls read;
- Number of attacks made and hits taken;
- Number of tiles traversed.

## Task 5 — Cartridge With a Battery

Implement the **datalayer** responsible for saving and loading game progress to a .json file.

**Requirements:**

- After completing each level, the game must save the current stats and level number.
- When the game is restarted and the player chooses to resume the last saved session, the levels must be regenerated based on the saved data, and the entire game state must be restored. This includes all collected points, current character attributes, and positions and states of all entities.
- The game must also persist the statistics of all playthroughs. When viewing the leaderboard, players should see their best runs, even if they did not successfully complete the game.

## Bonus Task 6 — You Shall Not Pass!

- Generate doors between rooms and corridors, as well as corresponding keys.
- Implement a colored key system inspired by classic DOOM mechanics.
- Use modified depth-first or breadth-first search algorithms to verify key accessibility and validity of generation (ensure there are no softlocks, or situations where progression becomes impossible).

## Bonus Task 7 — The Art of Balance

- Add a system of dynamic difficulty adjustment based on the player’s performance.
- If the player progresses too easily, the game should increase the difficulty.
- If the player struggles, the game may spawn more helpful items (e.g., additional healing if health is often low) or reduce the number and strength of enemies.

## Bonus Task 8 — Imagine You’re a Table

- Add a new enemy type: the **Mimic** (white m).
- Mimics disguise themselves as items.
- Attributes: high dexterity, low strength, high health, and low hostility.

## Bonus Task 9 — Full 3D

- Add a 3D rendering mode where:
  - The main view switches to a first-person 3D perspective.
  - The 2D view remains as a mini-map in the corner of the screen.
  - Controls are updated accordingly.  
      - W — move forward,  
      - S — move backward,  
      - A — turn left,  
      - D — turn right.
- Use Ray Casting and the curses library for the 3D rendering of rooms and corridors.
- Room and tunnel walls should have textures to clearly show player movement.
- A sample implementation of 3D level rendering can be found in the code-samples folder.