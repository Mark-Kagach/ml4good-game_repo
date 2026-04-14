# Alignment Adventure — Design Plan

## Concept
A Super Mario Bros-style 2D side-scrolling platformer that narrates the AI
safety career pipeline through Ilya Sutskever's timeline: Early OpenAI (2015)
→ The Blip (2023) → SSI & The Future (2024+). Retro 80s pixel art, neon
palette, scanline overlay, `pygame` primitives only (no external assets).

## Player
You are **ILYA SUTSKEVER**. Three hearts, power-up states, a stompable sprite
drawn from pygame rectangles (dark hair, glasses, cyan jacket).

## Power states (Mario-style)
| State  | Trigger                   | Ability                     |
|--------|---------------------------|-----------------------------|
| SMALL  | default / after fire hit  | stomp only                  |
| SUPER  | ALIGNMENT PATCH mushroom  | stomp, break bricks         |
| FIRE   | RLHF FLOWER               | stomp, break bricks, shoot HONEST SIGNALs |

Damage downgrades the power state before subtracting a heart. SAFETY STAR
gives ~6 seconds of invincibility on top of any state.

## Levels
1. **Early OpenAI** — 2015 tutorial. Walkers only, ? blocks with coins and a
   mushroom, decorative pipes. Friendly green theme.
2. **The Blip** — 2023 intermediate. Moving platforms, pipe gauntlet, a
   hidden SAFETY STAR, Shady Greg phasing in and out, MSFT lawyer hoppers,
   Twitter trolls, and a fire flower behind a brick. Purple/magenta theme.
3. **SSI & The Future** — 2024+ finale. Supply-depot mid-level with a full
   power-up set (mushroom + star + flower), a coin timing gap, then a boss
   arena where **SCAMA ALTMAN** patrols a floor flanked by two raised
   pedestals the player drops down from. SCAMA takes 3 stomps. Portal
   unlocks after the required badges are collected; flagpole gives a
   score bonus before the portal. Red theme.

## Tile characters
```
#  solid block              ?  question block (coin/power-up)
b  brick (breakable super)  o  coin
c  badge collectible        !  spike hazard
w  walker enemy             h  hopper enemy
d  drone enemy              M  horizontal moving platform
V  vertical moving platform T  pipe top (solid)
t  pipe body (solid)        F  flagpole
P  player spawn             E  portal goal
B  SCAMA boss               g  Shady Greg
a  e/acc zealot             x  CCP spy drone
$  $10B funding money-bag
```

## Controls
- **Arrows / WASD** — move
- **Space / W / Up** — jump
- **X / J** — throw HONEST SIGNAL (fire state only)
- **Enter** — start / retry
- **Esc** — title / quit

## Scoring
- Badge (`c`): 100
- Coin (`o`): 20
- Stomp enemy: 250 (boss: 500 per hit, 1500 defeated)
- Flagpole slide bonus: 100-500 depending on slide height

## Technical approach
- Single file `game.py`, 960×540 window, 60 FPS.
- Tile-based level as 2D strings; one row = 40px; levels are wider than the
  viewport with a camera.
- All sprites drawn with pygame primitives, CRT scanline overlay.
- Lightweight physics: gravity, ground/platform collision, coyote-free
  jumping (press-to-jump only when grounded).
- Single Game class with states: MENU, PLAYING, GAME_OVER, WIN.

## Why Level 3 was broken before
SCAMA patrolled the same 8-tile platform that was the only path to the
portal, with a 2-tile ceiling (no room above to jump+stomp safely) plus
two tracking CCP drones and a charging e/acc zealot converging on the
approach. No power-ups, no raised stomp pad. The redesign gives the
player a supply depot earlier and a proper boss arena with stomp
pedestals so SCAMA becomes a skill check rather than a physics trap.
