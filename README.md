# super ilya bros

A retro 80s AI-safety platformer, built with `pygame`, that leans hard into
Super Mario Bros. You play **ILYA SUTSKEVER** across three levels that
retell the AI-safety career pipeline: Early OpenAI (2015) → The Blip
(2023) → SSI & The Future (2024+), with SCAMA ALTMAN as the final boss.

## Run

```powershell
uv venv --python 3.12
uv sync
uv run python game.py
```

## Controls

| Action                      | Keys                       |
|-----------------------------|----------------------------|
| Move                        | Arrows / `A` `D`           |
| Jump                        | `Space` / `W` / `Up`       |
| Shoot HONEST SIGNAL (fire)  | `X` / `J`                  |
| Mute / unmute music         | `M`                        |
| Start / retry               | `Enter`                    |
| Return to title / quit      | `Esc`                      |

## What's in there

- **Three scrolling levels**, each with its own palette, enemies, and signs
  narrating the lore.
- **`?` blocks** — bump from below for coins, ALIGNMENT PATCH (mushroom,
  +1 heart), SAFETY STAR (invincibility), or RLHF FLOWER (shoot fireballs).
- **Brick blocks** — solid until you're SUPER, then you can headbutt them
  into dust for score.
- **Coins** scattered across every level. 20 points each.
- **Flagpole** at the end of each level — touch it before the portal for
  a sliding bonus.
- **Power states:** SMALL → SUPER → FIRE. Damage downgrades your power
  before taking a heart. SAFETY STAR gives ~6s of full invincibility and
  lets you bodycheck enemies for points.
- **SCAMA ALTMAN** — final boss with 3 HP. Drop-stomp him from the two
  raised pedestals, or burn him down with fireballs. Pushed too far?
  Catch the emergency SAFETY STAR in the boss arena.
- **The usual suspects:** Shady Greg (phases in and out), e/acc Zealot
  (charges toward you), CCP Spy Drone (tracking), $10B Funding money-bag
  (hoppy).

## Level 3 was genuinely impossible before — what changed

The old boss fight stuck SCAMA on the only platform leading to the portal,
with two tracking CCP drones and a charging zealot converging on the same
tile, no power-ups anywhere, and no high ground to stomp from. The
redesigned level gives you a **supply depot** mid-level (mushroom, star,
fire flower in a row of `?` blocks), thins out the drones on the main
path, and finishes with a **proper boss arena:** flat floor between two
raised pedestals so you can drop-stomp SCAMA's head. Three good stomps
and he's done.

## Music and SFX

Every sound is **synthesized at startup** — no audio files shipped. On
launch you'll see `GENERATING CHIPTUNE...` for about a quarter-second
while we bake:

- A menu theme, a distinct loop per level, and short fanfares for win /
  lose — NES-style square lead, triangle bass, noise-based drums.
- Ten one-shot SFX: jump, coin, stomp, damage, powerup, fireball, brick
  break, portal, flagpole slide, block bump.

Press `M` in-game to toggle everything off/on.

## File layout

- `game.py` — game logic (player, enemies, level parser, level data, loop).
- `audio.py` — procedural chiptune + SFX synthesis.
- `plan.md` — design doc and rationale.
- `pyproject.toml` / `uv.lock` — deps (pygame + numpy).
