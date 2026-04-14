# AI Safety Mario - Implementation Plan

## Concept
A Mario-style 2D side-scrolling platformer with 3 levels representing the AI safety career pipeline. Player has 3 hearts. 80s retro pixel art style.

## Levels
1. **ML4Good** - Beginner level. Simple platforms, few enemies. Green/friendly theme. Enemies: "Misaligned Chatbots" (basic walkers). Collectibles: "Alignment Papers". End: reach the "Graduation Portal".
2. **MATS** - Medium difficulty. More complex platforming, moving platforms. Purple/neon theme. Enemies: "Reward Hackers" (faster, jump), "Hallucination Ghosts" (float). Collectibles: "Research Credits". End: reach the "Fellowship Portal".
3. **Full-Time Job** - Hard. Fast-paced, tricky jumps, more enemies. Red/intense theme. Enemies: "Rogue AGIs" (smart, fast), "Deceptive Agents" (appear/disappear). Collectibles: "Safety Publications". End: reach the "Lab Portal" to win.

## Core Mechanics
- Arrow keys / WASD to move, Space to jump
- 3 hearts displayed top-left
- Hit enemy = lose 1 heart, brief invincibility
- 0 hearts = game over screen with retry
- Collect items for score
- Reach end portal to advance level
- Simple physics: gravity, ground collision, platform collision

## Technical Approach
- **Single file**: `game.py` using pygame
- All graphics drawn with pygame primitives (no external assets needed)
- 800x600 window
- Tile-based level design (simple 2D arrays)
- Scrolling camera follows player
- Retro pixel font, neon colors, scanline effect for 80s vibe

## Architecture (single file)
```
- Constants & Colors
- Player class (sprite, movement, jump, hearts, invincibility)
- Enemy classes (different behaviors per type)
- Platform class
- Collectible class
- Portal class
- Level data (3 level layouts as tile maps)
- Camera class
- HUD (hearts, score, level name)
- Game states: MENU, PLAYING, GAME_OVER, WIN
- Main game loop
```

## Visual Style
- Dark backgrounds with neon accent colors (cyan, magenta, green)
- Pixel-art characters drawn with rectangles
- Scanline overlay effect
- Retro bitmap-style font
- Star/grid backgrounds
- CRT glow feel

## Timeline (fits in ~15 min agent work)
1. Set up pygame boilerplate + game loop
2. Player movement + physics
3. Level tile system + camera
4. Enemies with basic AI
5. Hearts, collectibles, portals
6. 3 level layouts
7. Menu, game over, win screens
8. 80s visual polish (colors, effects)
