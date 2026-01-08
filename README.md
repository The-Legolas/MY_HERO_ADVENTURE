# My Hero Adventure

**My Hero Adventure** is a Python-based, text-driven RPG built as a learning and portfolio project. Its primary focus is **code architecture, system design, and testable game logic**, rather than graphical presentation or content volume.

The game is fully playable, but its core purpose is to demonstrate how a **moderately complex project** can be structured cleanly using **plain Python**, without external dependencies or frameworks.

---

## Intended Audience

This repository is intended for:

- Developers learning Python
- Developers interested in game architecture and systems design
- Anyone who wants to look at a self made game engine

---

## Project Goals

This project emphasizes:

- Clear separation of responsibilities
- Modular, data-driven systems
- Readable and maintainable code
- Explicit logic over hidden magic
- Testability as a design constraint

> Game mechanics exist to support architectural clarity, not to obscure it.

---

## Core Features

### Procedural Dungeons

- Dungeons regenerate each in-game day
- Layout size scales with player progression
- Boss and miniboss placement is deterministic but varied
- Exploration depth influences encounter difficulty

### Turn-Based Combat

- ATB-style turn order derived from speed
- Explicit combat phases  
  *(planning → action → resolution)*
- Unified action system:
  - Attack
  - Skill
  - Defend
  - Item
  - Flee
  - Wait

### Status Effect System

- Turn-based ticking statuses
- Stackable and non-stackable effects
- Resistances, immunities, and vulnerabilities
- Status-driven interruptions and action prevention

### Enemy AI & Intent System

- Enemies plan actions ahead of execution
- Skills filtered by cooldowns and behavioral constraints
- Weighted decision-making based on intent
- Designed to be extended rather than rewritten

---

## Requirements

- **Python 3.12**
- No third-party libraries required  
  *(standard library only)*

---

## How to Run

If using the .sh files remember to first do

```bash
chmod +x {filename}
```

### Start the Game

```bash
./run_game.sh
```

Or manually:

```py
python3 main.py
```

Run Unit Tests

```bash
./run_tests.sh
```

Or manually:

```py
python3 -m unittest
```

Project Structure (High-Level)

```py
game/
├── core/                # Characters, enemies, items, statuses, skills
├── definitions/         # Various hard data for the classes
├── engine/              # Game loop, save/load, input handling, spawning logic
├── systems/combat/      # Combat, damage, combat logic
├── systems/enums/       # All enum classes
├── systems/util_funcs/  # Various util functions used throughout the code base
├── tests/               # Unit tests by system
├── ui/                  # Text rendering and menus
├── ui/dialog/           # All dialog is held here
├── world/               # Dungeon, town, world state
├── world/town_logic/    # Town creation, layout, shop systems
main.py
```

Each folder represents a **clear responsibility boundary**.  
Cross-system dependencies are intentional and kept minimal.

---

## Testing Philosophy

- Core logic is unit-tested; UI is not
- Tests validate **behavior**, not implementation details
- Randomness is isolated or controlled where required

---

## Contributions & Feedback

Feedback is welcome.

This project is not feature-request driven, but useful contributions include:

- Architectural improvements
- Better test coverage
- Bug fixes
- Documentation improvements
- Design discussions

You are welcome to open issues simply to share thoughts or observations.

---

## License

No license has been chosen yet.

This means:

- The code is available for reading and learning
- Redistribution or commercial use is **not permitted unless explicitly asked for**

---


## Why I Built This

I built **My Hero Adventure** primarily for myself.

When learning, I kept running into the same problem:

> Small tutorials were too narrow to feel real,
> While larger projects were too complex to learn from meaningfully.

I needed something in between—something I could fully own, break, rebuild, and understand end to end.

This project exists to fill that space for me:

- Large enough to require real structure and discipline  
- Small enough that I can still reason about the whole system  
- Opinionated enough to force decisions, without locking me in  

The goal was to create a project where *I* could learn by doing, by making mistakes, and by iterating on something that grows over time.

If someone else happens to learn something from reading this code, that’s a welcome side effect—but the real success is that I’ve already learned more from building it than I would have from following another tutorial.

