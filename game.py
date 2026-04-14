"""
ALIGNMENT ADVENTURE 1987
Navigate the AI Safety career pipeline as ILYA SUTSKEVER.
Dodge SCAMA ALTMAN, e/acc zealots, CCP spy drones, Shady Greg,
and an army of misaligned agents.
"""
import math
import random
import sys

import pygame

from audio import Audio


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TILE_SIZE = 40
GRAVITY = 0.58
MOVE_SPEED = 4.6
JUMP_SPEED = 12.2
MAX_FALL_SPEED = 16
PLAYER_WIDTH = 28
PLAYER_HEIGHT = 36
INVINCIBLE_MS = 1200
LEVEL_CLEAR_HEAL = 1

BLACK = (10, 10, 18)
WHITE = (245, 245, 250)
OFF_WHITE = (230, 235, 240)
CYAN = (72, 236, 255)
MAGENTA = (255, 96, 180)
GREEN = (78, 255, 138)
YELLOW = (255, 228, 112)
RED = (255, 96, 108)
ORANGE = (255, 168, 56)
GOLD = (255, 215, 0)


def _build_rows(width, height, cells):
    """Compile a level tilemap. `cells` is a list of (row, col, char)."""
    grid = [["."] * width for _ in range(height)]
    for row, col, char in cells:
        if 0 <= row < height and 0 <= col < width:
            grid[row][col] = char
    return ["".join(r) for r in grid]


def _fill_row(cells, row, cols, char):
    for c in cols:
        cells.append((row, c, char))


def _fill_rect(cells, rows, cols, char):
    for r in rows:
        for c in cols:
            cells.append((r, c, char))


# ----------------------------- LEVEL 1 ------------------------------------
# Early OpenAI — tutorial with a real up/down route, staircases, pipes, and
# a handful of enemies distributed across three vertical tiers.
_L1_W, _L1_H = 100, 14
_l1 = []
# Full ground with one small tutorial pit (so "down" means something)
_fill_row(_l1, 13, range(_L1_W), "#")
for c in range(36, 39):
    _l1 = [cell for cell in _l1 if not (cell[0] == 13 and cell[1] == c)]
# Spawn platform
_fill_row(_l1, 8, range(0, 10), "#")
_l1 += [(6, 5, "P")]

# SECTION A — warm-up ? row + coin hints + first walker
_l1 += [(4, 12, "?"), (4, 14, "?"), (4, 16, "?")]
_l1 += [(6, 13, "o"), (6, 15, "o"), (6, 17, "o")]
_l1 += [(12, 14, "w")]

# SECTION B — ascending staircase (rows 10-12) onto a row-8 platform
_l1 += [(12, 20, "#"), (12, 21, "#"), (12, 22, "#"), (12, 23, "#")]
_l1 += [(11, 21, "#"), (11, 22, "#"), (11, 23, "#")]
_l1 += [(10, 22, "#"), (10, 23, "#")]
_l1 += [(9, 23, "#")]
_fill_row(_l1, 8, range(26, 32), "#")
_l1 += [(7, 26, "o"), (7, 28, "o"), (7, 30, "o")]  # coin trail on platform
_l1 += [(4, 28, "?")]
_l1 += [(6, 29, "c")]  # Badge 1 (up high)
_l1 += [(7, 28, "h")]  # hopper on the platform (overrides the coin on (7,28), that's fine)

# SECTION C — floating island over a ground pit (forces a jump).
# Extended to col 44 so the player can reach the row-8 high route in
# section D with a short jump off the right edge (jump reach same-row
# ≈184 px covers 40 px easily).
_fill_row(_l1, 10, range(34, 45), "#")
_l1 += [(9, 36, "h")]  # hopper patrols the island
_l1 += [(7, 35, "o"), (7, 37, "o"), (7, 39, "o")]
_l1 += [(4, 37, "?")]

# SECTION D — high route w/ brick cluster
_fill_row(_l1, 8, range(46, 56), "#")
_l1 += [(5, 48, "b"), (5, 49, "b"), (5, 50, "?"), (5, 51, "b"), (5, 52, "b")]
_l1 += [(7, 47, "w"), (7, 53, "w")]  # two walkers on the wide platform
_l1 += [(6, 58, "d")]  # drone hovers in the gap beyond

# SECTION E — low-ground coin gallery + short pipe
_l1 += [(12, 60, "c")]  # Badge 2 at ground level
_l1 += [(11, 64, "T"), (11, 65, "T"), (12, 64, "t"), (12, 65, "t")]
_l1 += [(10, 64, "o"), (10, 65, "o")]
_l1 += [(12, 68, "h")]

# SECTION F — jumpable pipe with coins on top (3 tiles so the player can
# actually land on it from ground — a 4-tile pipe is unreachable)
_l1 += [(10, 72, "T"), (10, 73, "T")]
for r in (11, 12):
    _l1 += [(r, 72, "t"), (r, 73, "t")]
_l1 += [(9, 72, "o"), (9, 73, "o")]  # reward for jumping on top

# SECTION G — descending staircase w/ coin trail
_l1 += [(12, 78, "#"), (12, 79, "#"), (12, 80, "#")]
_l1 += [(11, 78, "#"), (11, 79, "#")]
_l1 += [(10, 78, "#")]
_l1 += [(9, 78, "o"), (10, 79, "o"), (11, 80, "o")]
_l1 += [(12, 84, "w")]

# SECTION H — final approach on row 10 (reachable from ground — row 8
# was too high to climb back up to after the descending staircase).
_fill_row(_l1, 10, range(82, 94), "#")
_l1 += [(9, 87, "o"), (9, 89, "o"), (9, 91, "o"), (9, 93, "o")]
_l1 += [(4, 90, "?")]
_l1 += [(6, 90, "c")]  # Badge 3 — jump from the row-10 platform
_l1 += [(7, 85, "d")]  # drone patrols above the platform

# Flag + portal
_l1 += [(12, 95, "F"), (11, 98, "E")]

LEVEL1_QUESTION_REWARDS = {
    (12, 4): "coin",
    (14, 4): "mushroom",
    (16, 4): "coin",
    (28, 4): "coin",
    (37, 4): "coin",
    (50, 5): "flower",     # hidden inside brick cluster
    (90, 4): "coin",
}

# ----------------------------- LEVEL 2 ------------------------------------
# The Blip — moving platforms, pipe gauntlet, more enemies, star + fireflower.
_L2_W, _L2_H = 100, 14
_l2 = []
# Ground with TWO pits
_fill_row(_l2, 13, range(_L2_W), "#")
# carve pits (remove ground)
for pit_cols in (range(22, 26), range(56, 59), range(80, 83)):
    for c in pit_cols:
        _l2 = [cell for cell in _l2 if not (cell[0] == 13 and cell[1] == c)]
# Platforms
_fill_row(_l2, 8, range(0, 10), "#")
_fill_row(_l2, 8, range(27, 34), "#")
_fill_row(_l2, 8, range(43, 50), "#")
_fill_row(_l2, 8, range(60, 68), "#")
_fill_row(_l2, 8, range(72, 79), "#")
_fill_row(_l2, 8, range(85, 93), "#")
# Spawn, flag, portal
_l2 += [(6, 5, "P"), (12, 90, "F"), (11, 95, "E")]
# Moving platforms
_l2 += [(10, 22, "M"), (10, 56, "M"), (9, 80, "M")]
# Vertical moving platform as an elevator near mid
_l2 += [(9, 53, "V")]
# ? blocks
_l2 += [(4, 13, "?"), (4, 15, "?"), (4, 34, "?"), (4, 64, "?"), (4, 78, "?"), (4, 88, "?")]
# Brick cluster with hidden fireflower
_l2 += [(5, 44, "b"), (5, 45, "?"), (5, 46, "b"), (5, 47, "b"), (5, 48, "?"), (5, 49, "b")]
# Coins
_fill_row(_l2, 6, (17, 19, 21, 30, 32, 46, 47, 62, 64, 66, 76, 77, 86, 88, 91), "o")
# Badges (3 required, one safely reachable, one moderate, one after gauntlet)
_l2 += [(10, 30, "c"), (10, 65, "c"), (4, 90, "c")]
# Enemies (base set)
_l2 += [(12, 28, "w"), (12, 42, "h"), (12, 50, "g"), (12, 66, "$"), (12, 76, "w"), (12, 86, "h")]
# Extra enemies for chaos
_l2 += [(12, 12, "w"), (7, 45, "d"), (6, 74, "d"), (12, 94, "g")]
# Pipes (gauntlet): 2 side-by-side pipe pairs
_l2 += [(11, 38, "T"), (11, 39, "T"), (12, 38, "t"), (12, 39, "t")]
_l2 += [(10, 70, "T"), (10, 71, "T"), (11, 70, "t"), (11, 71, "t"), (12, 70, "t"), (12, 71, "t")]
# Breakable brick ceiling above the row-8 platform at cols 27-34 so the
# player can actually reach it (from ground jump apex bottom=392 < row 6
# brick bottom=280 — unreachable without a platform to jump from)
_l2 += [(6, 29, "b"), (6, 30, "b"), (6, 31, "b"), (6, 32, "b")]
# Coins revealed once the bricks break
_l2 += [(4, 29, "o"), (4, 30, "o"), (4, 31, "o"), (4, 32, "o")]
# Extra ? block near the pipe gauntlet
_l2 += [(4, 40, "?")]

LEVEL2_QUESTION_REWARDS = {
    (13, 4): "coin",
    (15, 4): "star",
    (34, 4): "coin",
    (40, 4): "mushroom",   # extra pre-pit mushroom
    (64, 4): "coin",
    (78, 4): "mushroom",
    (88, 4): "coin",
    (45, 5): "flower",
    (48, 5): "coin",
}

# ----------------------------- LEVEL 3 ------------------------------------
# SSI & The Future — supply depot, gauntlet, boss arena (actually beatable).
_L3_W, _L3_H = 100, 14
_l3 = []
_fill_row(_l3, 13, range(_L3_W), "#")
# Remove ground for one pit in gauntlet (cols 40-42)
for c in range(40, 43):
    _l3 = [cell for cell in _l3 if not (cell[0] == 13 and cell[1] == c)]
# Spawn platform
_fill_row(_l3, 8, range(0, 10), "#")
# Stepping stone so the supply depot (row 8) is reachable from the row-8
# spawn (10-col gap is too wide for a direct jump)
_fill_row(_l3, 10, range(14, 19), "#")
# Supply depot platform (cols 20-33): safe elevated ground w/ power-ups
_fill_row(_l3, 8, range(20, 34), "#")
# Gauntlet mid-platform — row 10 so it's reachable from ground
_fill_row(_l3, 10, range(52, 60), "#")
# Boss arena: two pedestals so the player can drop-stomp SCAMA. 3 tiles
# tall (rows 10-12) — a 4-tile pedestal is unreachable from ground so the
# player would be walled in.
_fill_rect(_l3, range(10, 13), range(63, 66), "#")  # left pedestal
_fill_rect(_l3, range(10, 13), range(77, 80), "#")  # right pedestal
# Post-boss platform — row 10 (reachable from ground), extended left
# toward the right pedestal so the transition isn't a cruel gap
_fill_row(_l3, 10, range(82, 95), "#")
# Spawn / flag / portal
_l3 += [(6, 5, "P"), (12, 94, "F"), (11, 97, "E")]
# ? blocks - opening (intro coin)
_l3 += [(4, 12, "?")]
# Supply depot ? blocks (mushroom, star, flower)
_l3 += [(4, 22, "?"), (4, 25, "?"), (4, 28, "?")]
# Boss arena ? blocks: coin + star for emergency
_l3 += [(4, 65, "?"), (4, 78, "?")]
# (previously had a brick cluster at (5, 48-50) but the nearest platforms
# were too far to head-bump from, so it was unreachable and removed)
# Moving platform spans the pit (col 40-42)
_l3 += [(11, 38, "M")]
# Coins
_fill_row(_l3, 6, (14, 23, 26, 29, 45, 57, 64, 67, 74, 77, 88, 90, 92), "o")
# Badges (3 required). Avoid (10, 17) / (4, 45) / (8, 88) — all embedded
# in solid blocks or out of reach. New spots are all reachable:
#   (12, 17) — floats above ground near stepping stone (walk-collect)
#   (6, 55)  — above the gauntlet row-10 platform (jump from it)
#   (6, 88)  — above the row-10 end platform (jump from it)
_l3 += [(12, 17, "c"), (6, 55, "c"), (6, 88, "c")]
# Enemies (reduce density along the main path, concentrate in gauntlet)
_l3 += [
    (12, 14, "w"),       # opening walker
    (12, 38, "h"),       # pre-pit hopper
    (9, 45, "x"),        # CCP drone hovering over gauntlet (avoid)
    (12, 50, "a"),       # e/acc zealot charges
    (12, 55, "h"),       # hopper on mid-platform
    (12, 70, "B"),       # SCAMA BOSS in arena
]

LEVEL3_QUESTION_REWARDS = {
    (12, 4): "coin",
    (22, 4): "mushroom",
    (25, 4): "star",
    (28, 4): "flower",
    (65, 4): "coin",
    (78, 4): "star",  # emergency star mid-boss
}


LEVEL_DEFS = [
    {
        "name": "Early OpenAI",
        "subtitle": "2015. Ilya joins OpenAI. Elon writes checks. Dreams are pure.",
        "bg_top": (12, 18, 30),
        "bg_bottom": (6, 10, 18),
        "accent": GREEN,
        "grid": (30, 120, 78),
        "block": (38, 70, 56),
        "block_top": (88, 210, 134),
        "portal": (108, 255, 170),
        "badge": (156, 255, 190),
        "required_badges": 3,
        "collectible_label": "ARXIV PAPER",
        "hazard_label": "GRAD STUDENT DEBT",
        "walker_label": "GPT-1 BUG",
        "hopper_label": "BATCH NORM",
        "drone_label": "VANISHING GRAD",
        "rows": _build_rows(_L1_W, _L1_H, _l1),
        "question_rewards": LEVEL1_QUESTION_REWARDS,
        "signs": [
            (180, 100, "OPENAI EST. 2015"),
            (700, 100, "ELON'S $1B PLEDGE"),
            (1300, 100, "ILYA JOINS THE LAB"),
            (1900, 100, "GPT-1 IS BORN"),
            (2500, 100, "SCALING HYPOTHESIS"),
            (3200, 100, "NONPROFIT DREAMS ->"),
            (3700, 100, "KEEP ALIGNMENT PURE"),
        ],
    },
    {
        "name": "The Blip",
        "subtitle": "2023. The board fires Sam. Greg vanishes. Chaos reigns. Ilya signs.",
        "bg_top": (18, 8, 34),
        "bg_bottom": (8, 4, 18),
        "accent": MAGENTA,
        "grid": (120, 35, 110),
        "block": (70, 34, 82),
        "block_top": (232, 116, 255),
        "portal": (255, 146, 242),
        "badge": (255, 206, 102),
        "required_badges": 3,
        "collectible_label": "BOARD VOTE",
        "hazard_label": "LEAKED MEMO",
        "walker_label": "TWITTER TROLL",
        "hopper_label": "MSFT LAWYER",
        "drone_label": "NEWS DRONE",
        "rows": _build_rows(_L2_W, _L2_H, _l2),
        "question_rewards": LEVEL2_QUESTION_REWARDS,
        "signs": [
            (180, 100, "NOV 17 2023"),
            (500, 100, "SAM IS FIRED!!"),
            (820, 100, "ILYA: I DEEPLY REGRET"),
            (1200, 100, "GREG GOES DARK"),
            (1600, 100, "700 EMPLOYEES SIGN"),
            (2100, 100, "MICROSOFT CIRCLING"),
            (2650, 100, "THE BOARD CAVES"),
            (3200, 100, "SURVIVE THE COUP ->"),
        ],
    },
    {
        "name": "SSI & The Future",
        "subtitle": "2024+. Ilya founds SSI. SCAMA rebuilds. The real fight begins.",
        "bg_top": (36, 10, 14),
        "bg_bottom": (15, 4, 8),
        "accent": RED,
        "grid": (135, 34, 45),
        "block": (84, 34, 42),
        "block_top": (255, 124, 134),
        "portal": (255, 204, 84),
        "badge": (255, 244, 168),
        "required_badges": 3,
        "collectible_label": "SAFETY PUB",
        "hazard_label": "PROD OUTAGE",
        "walker_label": "SCALING MAXI",
        "hopper_label": "LOBBY DRONE",
        "drone_label": "CCP SPY DRONE",
        "rows": _build_rows(_L3_W, _L3_H, _l3),
        "question_rewards": LEVEL3_QUESTION_REWARDS,
        "signs": [
            (180, 100, "ILYA FOUNDS SSI"),
            (900, 100, "SUPPLY DEPOT ->"),
            (1500, 100, "SCAMA INBOUND"),
            (2100, 100, "e/acc VS DOOMERS"),
            (2650, 100, "BOSS ARENA"),
            (3400, 100, "AGI BY TUESDAY LOL"),
            (3800, 100, "ALIGNMENT LAB ->"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def draw_label(surface, text, x, y, color, font):
    """Draw a small floating label above an entity."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    # dark background pill
    bg = rect.inflate(8, 4)
    s = pygame.Surface((bg.w, bg.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, 160), (0, 0, bg.w, bg.h), border_radius=4)
    surface.blit(s, bg.topleft)
    surface.blit(rendered, rect)


# ---------------------------------------------------------------------------
# Game entities
# ---------------------------------------------------------------------------
class Collectible:
    def __init__(self, x, y, color, label):
        self.rect = pygame.Rect(x + 10, y + 10, 20, 20)
        self.base_y = self.rect.y
        self.color = color
        self.label = label
        self.phase = random.random() * math.tau
        self.collected = False

    def update(self):
        bob = math.sin(pygame.time.get_ticks() * 0.005 + self.phase) * 3
        self.rect.y = self.base_y + int(bob)

    def draw(self, surface, camera_x, camera_y, font):
        if self.collected:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.rect(surface, self.color, (x, y, self.rect.w, self.rect.h), border_radius=4)
        pygame.draw.rect(surface, WHITE, (x + 6, y + 4, 8, 12), border_radius=2)
        pygame.draw.rect(surface, (255, 255, 255, 70), (x + 2, y + 2, self.rect.w - 4, 4), border_radius=2)
        draw_label(surface, self.label, x + self.rect.w // 2, y - 10, self.color, font)


class Hazard:
    def __init__(self, x, y, color, label):
        self.rect = pygame.Rect(x + 4, y + 12, TILE_SIZE - 8, TILE_SIZE - 12)
        self.color = color
        self.label = label

    def draw(self, surface, camera_x, camera_y, font):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        points = [
            (x, y + self.rect.h),
            (x + self.rect.w * 0.2, y + 10),
            (x + self.rect.w * 0.4, y + self.rect.h),
            (x + self.rect.w * 0.6, y + 6),
            (x + self.rect.w * 0.8, y + self.rect.h),
            (x + self.rect.w, y + 12),
            (x + self.rect.w, y + self.rect.h),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, YELLOW, points, 2)
        draw_label(surface, self.label, x + self.rect.w // 2, y - 6, RED, font)


class MovingPlatform:
    def __init__(self, x, y, axis, accent):
        self.rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE // 2)
        self.origin = pygame.Vector2(x, y)
        self.axis = axis
        self.speed = 1.6
        self.span = TILE_SIZE * 4
        self.direction = 1
        self.delta = pygame.Vector2()
        self.accent = accent

    def update(self):
        old_x, old_y = self.rect.x, self.rect.y
        if self.axis == "x":
            self.rect.x += int(self.speed * self.direction)
            if abs(self.rect.x - self.origin.x) >= self.span:
                self.rect.x = int(self.origin.x + self.span * self.direction)
                self.direction *= -1
        else:
            self.rect.y += int(self.speed * self.direction)
            if abs(self.rect.y - self.origin.y) >= self.span:
                self.rect.y = int(self.origin.y + self.span * self.direction)
                self.direction *= -1
        self.delta.update(self.rect.x - old_x, self.rect.y - old_y)

    def draw(self, surface, camera_x, camera_y):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.rect(surface, self.accent, (x, y, self.rect.w, self.rect.h), border_radius=4)
        pygame.draw.rect(surface, WHITE, (x + 6, y + 4, self.rect.w - 12, 4), border_radius=2)


# ---------------------------------------------------------------------------
# Enemy classes
# ---------------------------------------------------------------------------
class Enemy:
    def __init__(self, x, y, palette, label):
        self.rect = pygame.Rect(x + 6, y + 6, TILE_SIZE - 12, TILE_SIZE - 6)
        self.start = pygame.Vector2(self.rect.topleft)
        self.vx = 0
        self.vy = 0
        self.palette = palette
        self.label = label
        self.alive = True
        self.direction = -1
        self.base_y = self.rect.y

    def draw_body(self, surface, camera_x, camera_y, body_color, eye_color):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.rect(surface, body_color, (x, y, self.rect.w, self.rect.h), border_radius=6)
        pygame.draw.rect(surface, eye_color, (x + 5, y + 7, 6, 6), border_radius=1)
        pygame.draw.rect(surface, eye_color, (x + self.rect.w - 11, y + 7, 6, 6), border_radius=1)
        pygame.draw.rect(surface, BLACK, (x + 6, y + self.rect.h - 8, self.rect.w - 12, 3), border_radius=2)


class WalkerEnemy(Enemy):
    def __init__(self, x, y, palette, speed, label):
        super().__init__(x, y, palette, label)
        self.vx = speed

    def update(self, level):
        if not self.alive:
            return
        self.vy = min(self.vy + GRAVITY * 0.9, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        front_x = self.rect.centerx + (self.rect.w // 2 + 4) * (1 if self.vx > 0 else -1)
        foot_y = self.rect.bottom + 4
        if not level.ground_at(front_x, foot_y):
            self.vx *= -1
        self.rect.y += int(self.vy)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0
        self.direction = 1 if self.vx > 0 else -1

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        self.draw_body(surface, camera_x, camera_y, self.palette["body"], self.palette["eye"])
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        draw_label(surface, self.label, x + self.rect.w // 2, y - 10, self.palette["body"], font)


class HopperEnemy(Enemy):
    def __init__(self, x, y, palette, label):
        super().__init__(x, y, palette, label)
        self.vx = 2.2
        self.jump_timer = random.randint(40, 100)

    def update(self, level):
        if not self.alive:
            return
        self.jump_timer -= 1
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        self.rect.y += int(self.vy)
        on_ground = False
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                    on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0
        if on_ground and self.jump_timer <= 0:
            self.vy = -9.8
            self.jump_timer = random.randint(75, 130)
        self.direction = 1 if self.vx > 0 else -1

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        self.draw_body(surface, camera_x, camera_y, self.palette["body"], self.palette["eye"])
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.rect(surface, WHITE, (x + 7, y + self.rect.h - 14, self.rect.w - 14, 4), border_radius=2)
        draw_label(surface, self.label, x + self.rect.w // 2, y - 10, self.palette["body"], font)


class DroneEnemy(Enemy):
    def __init__(self, x, y, palette, label):
        super().__init__(x, y, palette, label)
        self.span = TILE_SIZE * 3
        self.speed = 2.4
        self.phase = random.random() * math.tau

    def update(self, level):
        if not self.alive:
            return
        next_x = self.rect.x + int(self.speed * self.direction)
        if abs(next_x - self.start.x) > self.span:
            self.direction *= -1
            next_x = self.rect.x + int(self.speed * self.direction)
        self.rect.x = next_x
        self.rect.y = int(self.base_y + math.sin(pygame.time.get_ticks() * 0.008 + self.phase) * 18)

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.ellipse(surface, self.palette["body"], (x, y, self.rect.w, self.rect.h))
        pygame.draw.ellipse(surface, WHITE, (x + 6, y + 6, self.rect.w - 12, 10))
        pygame.draw.rect(surface, self.palette["eye"], (x + 7, y + self.rect.h - 10, self.rect.w - 14, 4), border_radius=2)
        draw_label(surface, self.label, x + self.rect.w // 2, y - 10, self.palette["body"], font)


class BossEnemy(Enemy):
    """SCAMA ALTMAN - big, fast, menacing. 3 stomps to defeat."""

    def __init__(self, x, y):
        palette = {"body": (255, 50, 30), "eye": GOLD}
        super().__init__(x, y, palette, "SCAMA ALTMAN")
        self.rect = pygame.Rect(x + 2, y - 6, TILE_SIZE + 4, TILE_SIZE + 6)
        self.start = pygame.Vector2(self.rect.topleft)
        self.vx = 2.4
        self.base_y = self.rect.y
        self.hp = 3
        self.hit_flash = 0
        self.base_speed = 2.4

    def hit(self):
        """Called on stomp. Returns True if killed."""
        self.hp -= 1
        self.hit_flash = 18
        # Rages faster as HP drops
        direction = 1 if self.vx >= 0 else -1
        self.vx = (self.base_speed + (3 - self.hp) * 0.9) * direction
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def update(self, level):
        if not self.alive:
            return
        self.vy = min(self.vy + GRAVITY * 0.9, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        front_x = self.rect.centerx + (self.rect.w // 2 + 4) * (1 if self.vx > 0 else -1)
        foot_y = self.rect.bottom + 4
        if not level.ground_at(front_x, foot_y):
            self.vx *= -1
        self.rect.y += int(self.vy)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        body_color = (180, 20, 10)
        if self.hit_flash > 0:
            self.hit_flash -= 1
            if self.hit_flash % 4 < 2:
                body_color = WHITE
        pygame.draw.rect(surface, body_color, (x, y, self.rect.w, self.rect.h), border_radius=8)
        # Evil golden eyes
        pygame.draw.rect(surface, GOLD, (x + 6, y + 10, 10, 8), border_radius=2)
        pygame.draw.rect(surface, GOLD, (x + self.rect.w - 16, y + 10, 10, 8), border_radius=2)
        pygame.draw.rect(surface, BLACK, (x + 8, y + 12, 4, 4))
        pygame.draw.rect(surface, BLACK, (x + self.rect.w - 12, y + 12, 4, 4))
        # Evil grin
        pygame.draw.rect(surface, WHITE, (x + 10, y + self.rect.h - 14, self.rect.w - 20, 5), border_radius=2)
        # Dollar signs on body
        dollar_surf = font.render("$$$", True, GOLD)
        surface.blit(dollar_surf, (x + 8, y + 24))
        # HP pips
        for i in range(self.hp):
            pygame.draw.rect(surface, GOLD, (x + 4 + i * 10, y - 10, 7, 5), border_radius=1)
            pygame.draw.rect(surface, (100, 60, 0), (x + 4 + i * 10, y - 10, 7, 5), 1, border_radius=1)
        # Label
        draw_label(surface, f"SCAMA ALTMAN x{self.hp}", x + self.rect.w // 2, y - 22, (255, 50, 30), font)


class ShadyGregEnemy(Enemy):
    """SHADY GREG BROCKMAN - phases in and out, unpredictable."""

    def __init__(self, x, y):
        palette = {"body": (100, 120, 180), "eye": WHITE}
        super().__init__(x, y, palette, "SHADY GREG")
        self.vx = 2.0
        self.visible = True
        self.phase_timer = random.randint(30, 80)

    def update(self, level):
        if not self.alive:
            return
        self.phase_timer -= 1
        if self.phase_timer <= 0:
            self.visible = not self.visible
            self.phase_timer = random.randint(40, 90)
        self.vy = min(self.vy + GRAVITY * 0.9, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        front_x = self.rect.centerx + (self.rect.w // 2 + 4) * (1 if self.vx > 0 else -1)
        foot_y = self.rect.bottom + 4
        if not level.ground_at(front_x, foot_y):
            self.vx *= -1
        self.rect.y += int(self.vy)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0

    @property
    def effective_rect(self):
        """Only collidable when visible."""
        if not self.visible:
            return pygame.Rect(0, 0, 0, 0)
        return self.rect

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        alpha = 200 if self.visible else 40
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.palette["body"], alpha), (0, 0, self.rect.w, self.rect.h), border_radius=6)
        # Shifty eyes
        pygame.draw.rect(s, (*WHITE, alpha), (5, 7, 6, 6), border_radius=1)
        pygame.draw.rect(s, (*WHITE, alpha), (self.rect.w - 11, 7, 6, 6), border_radius=1)
        # Sunglasses (shady!)
        pygame.draw.rect(s, (*BLACK, alpha), (3, 5, self.rect.w - 6, 10), border_radius=3)
        pygame.draw.rect(s, (*(180, 180, 255), min(255, alpha + 50)), (5, 7, 6, 6), border_radius=1)
        pygame.draw.rect(s, (*(180, 180, 255), min(255, alpha + 50)), (self.rect.w - 11, 7, 6, 6), border_radius=1)
        surface.blit(s, (x, y))
        if self.visible:
            draw_label(surface, "SHADY GREG", x + self.rect.w // 2, y - 10, (100, 120, 180), font)
        else:
            draw_label(surface, "SHADY GREG (?)", x + self.rect.w // 2, y - 10, (60, 70, 100), font)


class EAccZealot(Enemy):
    """e/acc ZEALOT - fast rusher, charges toward player direction."""

    def __init__(self, x, y):
        palette = {"body": (255, 140, 0), "eye": RED}
        super().__init__(x, y, palette, "e/acc ZEALOT")
        self.vx = 3.5
        self.base_speed = 3.5

    def update(self, level, player_x=None):
        if not self.alive:
            return
        # Rush toward player if nearby
        if player_x is not None and abs(player_x - self.rect.x) < 300:
            self.vx = self.base_speed * 1.8 * (1 if player_x > self.rect.x else -1)
        self.vy = min(self.vy + GRAVITY * 0.9, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        front_x = self.rect.centerx + (self.rect.w // 2 + 4) * (1 if self.vx > 0 else -1)
        foot_y = self.rect.bottom + 4
        if not level.ground_at(front_x, foot_y):
            self.vx *= -1
        self.rect.y += int(self.vy)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        # Orange/fire body
        pygame.draw.rect(surface, (255, 100, 0), (x, y, self.rect.w, self.rect.h), border_radius=6)
        # Crazy eyes
        pygame.draw.rect(surface, RED, (x + 4, y + 6, 8, 8), border_radius=2)
        pygame.draw.rect(surface, RED, (x + self.rect.w - 12, y + 6, 8, 8), border_radius=2)
        pygame.draw.rect(surface, YELLOW, (x + 6, y + 8, 4, 4))
        pygame.draw.rect(surface, YELLOW, (x + self.rect.w - 10, y + 8, 4, 4))
        # "e/acc" on body
        acc_surf = font.render("e/acc", True, YELLOW)
        surface.blit(acc_surf, (x + 2, y + 18))
        draw_label(surface, "e/acc ZEALOT", x + self.rect.w // 2, y - 10, ORANGE, font)


class MoneyBagEnemy(Enemy):
    """MONEY BAG - bouncing bag of VC money corrupting everything."""

    def __init__(self, x, y):
        palette = {"body": GOLD, "eye": BLACK}
        super().__init__(x, y, palette, "$10B FUNDING")
        self.vx = 1.8
        self.jump_timer = random.randint(20, 60)

    def update(self, level):
        if not self.alive:
            return
        self.jump_timer -= 1
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        if any(self.rect.colliderect(tile) for tile in level.blocking_rects()):
            self.rect.x -= int(self.vx)
            self.vx *= -1
        self.rect.y += int(self.vy)
        on_ground = False
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                    on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0
        if on_ground and self.jump_timer <= 0:
            self.vy = -11
            self.jump_timer = random.randint(30, 70)

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        # Gold bag shape
        pygame.draw.rect(surface, GOLD, (x + 2, y + 6, self.rect.w - 4, self.rect.h - 6), border_radius=8)
        pygame.draw.rect(surface, (200, 170, 0), (x + 6, y, 16, 10), border_radius=4)
        # Dollar sign
        dollar = font.render("$", True, BLACK)
        surface.blit(dollar, (x + 10, y + 12))
        draw_label(surface, "$10B FUNDING", x + self.rect.w // 2, y - 10, GOLD, font)


class CCPSpyDrone(Enemy):
    """CCP SPY DRONE - tracking drone, follows player X."""

    def __init__(self, x, y):
        palette = {"body": (220, 40, 40), "eye": YELLOW}
        super().__init__(x, y, palette, "CCP SPY")
        self.span = TILE_SIZE * 5
        self.speed = 2.8
        self.phase = random.random() * math.tau

    def update(self, level, player_x=None):
        if not self.alive:
            return
        if player_x is not None and abs(player_x - self.rect.x) < 400:
            # Track toward player
            if player_x > self.rect.x:
                self.rect.x += int(self.speed * 0.8)
            else:
                self.rect.x -= int(self.speed * 0.8)
        else:
            next_x = self.rect.x + int(self.speed * self.direction)
            if abs(next_x - self.start.x) > self.span:
                self.direction *= -1
                next_x = self.rect.x + int(self.speed * self.direction)
            self.rect.x = next_x
        self.rect.y = int(self.base_y + math.sin(pygame.time.get_ticks() * 0.006 + self.phase) * 22)

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        # Red drone body
        pygame.draw.ellipse(surface, (200, 30, 30), (x, y, self.rect.w, self.rect.h))
        # Star symbol
        star_surf = font.render("*", True, YELLOW)
        surface.blit(star_surf, (x + 10, y + 4))
        # Antenna
        pygame.draw.line(surface, YELLOW, (x + self.rect.w // 2, y), (x + self.rect.w // 2, y - 8), 2)
        pygame.draw.circle(surface, RED, (x + self.rect.w // 2, y - 10), 3)
        draw_label(surface, "CCP SPY", x + self.rect.w // 2, y - 18, (220, 40, 40), font)


# ---------------------------------------------------------------------------
# Coins, Blocks, Power-ups, Fireballs, Flagpole (Mario-style)
# ---------------------------------------------------------------------------
class Coin:
    """Small collectible for score only. Separate from badges."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 12, y + 12, 16, 16)
        self.base_y = self.rect.y
        self.phase = random.random() * math.tau
        self.collected = False

    def update(self):
        bob = math.sin(pygame.time.get_ticks() * 0.008 + self.phase) * 3
        self.rect.y = self.base_y + int(bob)

    def draw(self, surface, camera_x, camera_y):
        if self.collected:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        pygame.draw.ellipse(surface, GOLD, (x, y, self.rect.w, self.rect.h))
        pygame.draw.ellipse(surface, (255, 235, 120), (x + 3, y + 2, self.rect.w - 6, self.rect.h - 6))
        pygame.draw.line(surface, (140, 100, 0), (x + self.rect.w // 2, y + 3),
                         (x + self.rect.w // 2, y + self.rect.h - 3), 2)


class QuestionBlock:
    """Hit from below: pops a coin, mushroom, star, or flower."""

    def __init__(self, x, y, reward="coin"):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.reward = reward  # "coin", "mushroom", "star", "flower"
        self.spent = False
        self.bump_frames = 0
        self.spawn_request = None  # set to reward when triggered
        self.phase = random.random() * math.tau

    def bump(self):
        """Called when player's head strikes underneath. Returns reward string or None."""
        if self.spent:
            return None
        self.spent = True
        self.bump_frames = 10
        self.spawn_request = self.reward
        return self.reward

    def update(self):
        if self.bump_frames > 0:
            self.bump_frames -= 1

    def draw(self, surface, camera_x, camera_y, font):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        if self.bump_frames > 0:
            y -= 6
        if self.spent:
            # spent block = dull brown brick
            pygame.draw.rect(surface, (120, 80, 40), (x, y, self.rect.w, self.rect.h), border_radius=4)
            pygame.draw.rect(surface, (80, 50, 20), (x + 2, y + 2, self.rect.w - 4, self.rect.h - 4), 2, border_radius=3)
        else:
            pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006 + self.phase))
            body = (int(220 * pulse + 35), int(168 * pulse + 35), int(30 * pulse + 10))
            pygame.draw.rect(surface, body, (x, y, self.rect.w, self.rect.h), border_radius=4)
            pygame.draw.rect(surface, (60, 30, 10), (x, y, self.rect.w, self.rect.h), 2, border_radius=4)
            # studs in corners
            for dx, dy in ((4, 4), (self.rect.w - 8, 4), (4, self.rect.h - 8), (self.rect.w - 8, self.rect.h - 8)):
                pygame.draw.rect(surface, (60, 30, 10), (x + dx, y + dy, 4, 4))
            # big white "?"
            q = font.render("?", True, WHITE)
            surface.blit(q, (x + self.rect.w // 2 - q.get_width() // 2, y + self.rect.h // 2 - q.get_height() // 2))


class Brick:
    """Solid brick. If player is Super/Fire, a head-bump from below breaks it."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.broken = False
        self.bump_frames = 0

    def bump(self, can_break):
        """Returns True if broken this frame."""
        if self.broken:
            return False
        if can_break:
            self.broken = True
            return True
        self.bump_frames = 8
        return False

    def update(self):
        if self.bump_frames > 0:
            self.bump_frames -= 1

    def draw(self, surface, camera_x, camera_y):
        if self.broken:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        if self.bump_frames > 0:
            y -= 4
        pygame.draw.rect(surface, (160, 70, 40), (x, y, self.rect.w, self.rect.h), border_radius=3)
        # brick pattern
        pygame.draw.line(surface, (90, 40, 20), (x, y + TILE_SIZE // 2), (x + TILE_SIZE, y + TILE_SIZE // 2), 2)
        pygame.draw.line(surface, (90, 40, 20), (x + TILE_SIZE // 2, y), (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 2)
        pygame.draw.line(surface, (90, 40, 20), (x + TILE_SIZE // 4, y + TILE_SIZE // 2),
                         (x + TILE_SIZE // 4, y + TILE_SIZE), 2)
        pygame.draw.line(surface, (90, 40, 20), (x + 3 * TILE_SIZE // 4, y + TILE_SIZE // 2),
                         (x + 3 * TILE_SIZE // 4, y + TILE_SIZE), 2)
        pygame.draw.rect(surface, (60, 20, 10), (x, y, self.rect.w, self.rect.h), 2, border_radius=3)


class PowerUp:
    """Base class: mushroom / star / flower. Emerges from a ? block."""

    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x + 6, y + 4, 28, 28)
        self.kind = kind  # "mushroom", "star", "flower"
        self.vx = 2.0
        self.vy = 0.0
        self.emerging = True
        self.emerge_target_y = y - TILE_SIZE + 4
        self.alive = True

    def update(self, level):
        if not self.alive:
            return
        if self.emerging:
            self.rect.y -= 1
            if self.rect.y <= self.emerge_target_y:
                self.emerging = False
            return
        if self.kind == "star":
            # bouncy: gravity + auto-hop on ground
            self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        else:
            self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                self.rect.x -= int(self.vx)
                self.vx *= -1
                break
        self.rect.y += int(self.vy)
        landed = False
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = 0
                    landed = True
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy = 0
        if landed and self.kind == "star":
            self.vy = -9.0
        if self.rect.top > level.pixel_height + 80:
            self.alive = False

    def draw(self, surface, camera_x, camera_y, font):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        if self.kind == "mushroom":
            # red cap with white spots, cream stem
            pygame.draw.rect(surface, (255, 240, 220), (x + 4, y + 14, self.rect.w - 8, self.rect.h - 14), border_radius=4)
            pygame.draw.ellipse(surface, (230, 40, 40), (x, y, self.rect.w, 20))
            pygame.draw.circle(surface, WHITE, (x + 8, y + 10), 3)
            pygame.draw.circle(surface, WHITE, (x + self.rect.w - 8, y + 10), 3)
            pygame.draw.rect(surface, BLACK, (x + 10, y + 20, 3, 3))
            pygame.draw.rect(surface, BLACK, (x + self.rect.w - 13, y + 20, 3, 3))
            draw_label(surface, "ALIGNMENT PATCH", x + self.rect.w // 2, y - 8, (230, 40, 40), font)
        elif self.kind == "star":
            # pulsing yellow star
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.02)
            color = (255, int(200 + 55 * pulse), int(60 + 60 * pulse))
            cx, cy = x + self.rect.w // 2, y + self.rect.h // 2
            points = []
            for i in range(10):
                angle = -math.pi / 2 + i * math.pi / 5
                r = 14 if i % 2 == 0 else 6
                points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, WHITE, points, 2)
            draw_label(surface, "SAFETY STAR", x + self.rect.w // 2, y - 8, YELLOW, font)
        else:  # flower
            # orange petals + green stem
            cx, cy = x + self.rect.w // 2, y + self.rect.h // 2 - 2
            for angle_i in range(6):
                ang = angle_i * math.tau / 6
                px = cx + math.cos(ang) * 9
                py = cy + math.sin(ang) * 9
                pygame.draw.circle(surface, ORANGE, (int(px), int(py)), 5)
            pygame.draw.circle(surface, YELLOW, (cx, cy), 5)
            pygame.draw.rect(surface, GREEN, (cx - 2, cy + 8, 4, 10))
            draw_label(surface, "RLHF FLOWER", x + self.rect.w // 2, y - 8, ORANGE, font)


class Fireball:
    """Projectile thrown by Fire-state Ilya. Kills walkers/hoppers on contact."""

    SPEED = 7.0
    BOUNCE = -8.5

    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 14, 14)
        self.vx = self.SPEED * direction
        self.vy = 2.0
        self.alive = True
        self.bounces = 0
        self.phase = random.random() * math.tau

    def update(self, level):
        if not self.alive:
            return
        self.vy = min(self.vy + GRAVITY * 0.9, MAX_FALL_SPEED)
        self.rect.x += int(self.vx)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                self.alive = False
                return
        self.rect.y += int(self.vy)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.vy = self.BOUNCE
                    self.bounces += 1
                    if self.bounces > 3:
                        self.alive = False
                else:
                    self.alive = False
                    return
        if self.rect.top > level.pixel_height + 60:
            self.alive = False

    def draw(self, surface, camera_x, camera_y):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        flicker = (pygame.time.get_ticks() // 50) % 2
        outer = (255, 120 + flicker * 40, 30)
        inner = (255, 230, 100)
        pygame.draw.circle(surface, outer, (x + 7, y + 7), 7)
        pygame.draw.circle(surface, inner, (x + 7, y + 7), 4)


class Flagpole:
    """End-of-level flag. Touch to trigger slide + bonus."""

    def __init__(self, x, y):
        # y is the ground row's y value; pole rises 6 tiles above
        self.height = TILE_SIZE * 6
        self.rect = pygame.Rect(x + TILE_SIZE // 2 - 3, y - self.height, 6, self.height)
        self.base_y = y
        self.top_y = y - self.height
        self.flag_y = self.top_y + 10
        self.touched = False
        self.slide_done = False

    def slide_flag(self):
        target = self.base_y - 30
        if self.flag_y < target:
            self.flag_y = min(target, self.flag_y + 4)
        else:
            self.slide_done = True

    def draw(self, surface, camera_x, camera_y):
        x = self.rect.x - camera_x
        y_top = self.rect.y - camera_y
        y_base = self.base_y - camera_y
        # base block
        pygame.draw.rect(surface, (180, 180, 195), (x - 12, y_base - 12, 30, 12), border_radius=3)
        pygame.draw.rect(surface, (90, 90, 110), (x - 12, y_base - 12, 30, 12), 2, border_radius=3)
        # pole
        pygame.draw.rect(surface, (200, 210, 230), (x, y_top, 6, self.height))
        pygame.draw.circle(surface, GOLD, (x + 3, y_top - 2), 6)
        # flag (triangle) at current flag_y
        flag_y = self.flag_y - camera_y
        pygame.draw.polygon(surface, (80, 230, 140),
                            [(x + 6, flag_y), (x + 40, flag_y + 10), (x + 6, flag_y + 20)])
        pygame.draw.polygon(surface, WHITE,
                            [(x + 6, flag_y), (x + 40, flag_y + 10), (x + 6, flag_y + 20)], 1)


class Pipe:
    """Decorative/solid pipe; two tiles wide by `height` tiles tall."""

    def __init__(self, x, y, height):
        self.rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * height)

    def draw(self, surface, camera_x, camera_y):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        # lip (top)
        pygame.draw.rect(surface, (60, 200, 110), (x - 4, y, self.rect.w + 8, TILE_SIZE // 2), border_radius=4)
        pygame.draw.rect(surface, (30, 130, 70), (x - 4, y, self.rect.w + 8, TILE_SIZE // 2), 2, border_radius=4)
        # shaft
        pygame.draw.rect(surface, (40, 170, 90), (x, y + TILE_SIZE // 2, self.rect.w, self.rect.h - TILE_SIZE // 2))
        pygame.draw.rect(surface, (20, 100, 50), (x, y + TILE_SIZE // 2, self.rect.w, self.rect.h - TILE_SIZE // 2), 2)
        # highlights
        pygame.draw.rect(surface, (110, 255, 160), (x + 6, y + TILE_SIZE // 2 + 4, 6, self.rect.h - TILE_SIZE // 2 - 8))


# ---------------------------------------------------------------------------
# Portal
# ---------------------------------------------------------------------------
class Portal:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x + 6, y - TILE_SIZE, TILE_SIZE + 8, TILE_SIZE * 2)
        self.color = color

    def draw(self, surface, camera_x, camera_y, unlocked):
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        frame = self.color if unlocked else (100, 100, 110)
        fill = self.color if unlocked else (36, 36, 42)
        pygame.draw.rect(surface, frame, (x, y, self.rect.w, self.rect.h), border_radius=8)
        pygame.draw.rect(surface, fill, (x + 6, y + 8, self.rect.w - 12, self.rect.h - 14), border_radius=6)
        if unlocked:
            pygame.draw.circle(surface, WHITE, (x + self.rect.w // 2, y + self.rect.h // 2), 7)


# ---------------------------------------------------------------------------
# Player (ILYA SUTSKEVER)
# ---------------------------------------------------------------------------
class Player:
    HEART_CAP = 5

    def __init__(self, spawn):
        self.rect = pygame.Rect(spawn[0], spawn[1], PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel = pygame.Vector2()
        self.hearts = 3
        self.invincible_until = 0
        self.star_until = 0  # hard invincibility from SAFETY STAR
        self.on_ground = False
        self.badges = 0
        self.coins = 0
        self.score = 0
        self.facing = 1
        self.message = ""
        self.message_until = 0
        self.power = "small"  # "small", "super", "fire"
        self.fireballs = []
        self.shoot_cooldown = 0
        self.head_bumped_blocks = set()  # rect ids bumped this frame
        self.bumped_block = None  # the block rect bumped this frame
        self.reached_flag = False
        self.audio = None  # set by Game after construction

    def reset_position(self, spawn):
        self.rect.topleft = spawn
        self.vel.update(0, 0)
        self.on_ground = False

    def starred(self):
        return pygame.time.get_ticks() < self.star_until

    def damage(self, label):
        now = pygame.time.get_ticks()
        if self.starred():
            return False
        if now < self.invincible_until:
            return False
        # Power downgrade before heart loss
        if self.power == "fire":
            self.power = "super"
            self.invincible_until = now + INVINCIBLE_MS
            self.message = f"-FLOWER: {label}"
            self.message_until = now + 1200
            if self.audio:
                self.audio.play_sfx("damage")
            return False
        if self.power == "super":
            self.power = "small"
            self.invincible_until = now + INVINCIBLE_MS
            self.message = f"-PATCH: {label}"
            self.message_until = now + 1200
            if self.audio:
                self.audio.play_sfx("damage")
            return False
        self.hearts -= 1
        self.invincible_until = now + INVINCIBLE_MS
        self.message = f"-1 heart: {label}"
        self.message_until = now + 1400
        self.vel.x = -self.facing * 5
        self.vel.y = -6
        if self.audio:
            self.audio.play_sfx("damage")
        return True

    def bounce(self):
        self.vel.y = -9.6

    def pickup(self, kind):
        now = pygame.time.get_ticks()
        if kind == "mushroom":
            if self.hearts < self.HEART_CAP:
                self.hearts += 1
            if self.power == "small":
                self.power = "super"
            self.score += 300
            self.message = "+ALIGNMENT PATCH (+1 heart)"
            self.message_until = now + 1400
            if self.audio:
                self.audio.play_sfx("powerup")
        elif kind == "star":
            self.star_until = now + 6000
            self.score += 500
            self.message = "+SAFETY STAR - INVINCIBLE!"
            self.message_until = now + 1600
            if self.audio:
                self.audio.play_sfx("powerup")
        elif kind == "flower":
            self.power = "fire"
            self.score += 400
            self.message = "+RLHF FLOWER (press X/J)"
            self.message_until = now + 1600
            if self.audio:
                self.audio.play_sfx("powerup")
        elif kind == "coin":
            self.coins += 1
            self.score += 20
            if self.audio:
                self.audio.play_sfx("coin")

    def shoot(self):
        if self.power != "fire":
            return False
        if self.shoot_cooldown > 0:
            return False
        if len(self.fireballs) >= 3:
            return False
        fx = self.rect.centerx + self.facing * 12
        fy = self.rect.centery - 2
        self.fireballs.append(Fireball(fx, fy, self.facing))
        self.shoot_cooldown = 14
        if self.audio:
            self.audio.play_sfx("fireball")
        return True

    def update(self, level, keys):
        self.bumped_block = None
        self.head_bumped_blocks.clear()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        accel = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            accel = -MOVE_SPEED
            self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            accel = MOVE_SPEED
            self.facing = 1
        self.vel.x = accel
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel.y = -JUMP_SPEED
            self.on_ground = False
            if self.audio:
                self.audio.play_sfx("jump")
        if keys[pygame.K_x] or keys[pygame.K_j]:
            self.shoot()
        self.vel.y = min(self.vel.y + GRAVITY, MAX_FALL_SPEED)
        self.rect.x += int(self.vel.x)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vel.x > 0:
                    self.rect.right = tile.left
                elif self.vel.x < 0:
                    self.rect.left = tile.right

        self.on_ground = False
        previous_bottom = self.rect.bottom
        self.rect.y += int(self.vel.y)
        for tile in level.blocking_rects():
            if self.rect.colliderect(tile):
                if self.vel.y > 0 and previous_bottom <= tile.top + 8:
                    self.rect.bottom = tile.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.bottom
                    self.bumped_block = tile
                    self.head_bumped_blocks.add(id(tile))
                    self.vel.y = 0

        for platform in level.moving_platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y >= 0 and previous_bottom <= platform.rect.top + 8:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.rect.x += int(platform.delta.x)
                    self.rect.y += int(platform.delta.y)

        # Update fireballs
        for fb in self.fireballs:
            fb.update(level)
        self.fireballs = [fb for fb in self.fireballs if fb.alive]

    def draw(self, surface, camera_x, camera_y, font):
        now = pygame.time.get_ticks()
        blink = now < self.invincible_until and not self.starred() and (now // 90) % 2 == 0
        if blink:
            for fb in self.fireballs:
                fb.draw(surface, camera_x, camera_y)
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y

        # Star tint cycle
        if self.starred():
            tint = [CYAN, MAGENTA, YELLOW, GREEN][(now // 80) % 4]
        else:
            tint = None

        # Jacket color signals power state
        if self.power == "fire":
            jacket = (255, 120, 60)
        elif self.power == "super":
            jacket = GREEN
        else:
            jacket = CYAN
        if tint:
            jacket = tint

        skin = (248, 228, 210)
        skin_shadow = (222, 200, 185)
        hair = (55, 40, 30) if not tint else tint
        glass = (35, 35, 52)

        # --- Head (pale, balding, tall forehead) -------------------------
        # Wide forehead block so the bald top is prominent
        pygame.draw.rect(surface, skin, (x + 4, y + 1, 20, 22), border_radius=7)
        # Subtle highlight across the bald pate
        pygame.draw.rect(surface, (255, 240, 225), (x + 8, y + 2, 12, 4), border_radius=2)
        # Jaw shadow under the chin
        pygame.draw.rect(surface, skin_shadow, (x + 6, y + 20, 16, 3), border_radius=2)

        # --- Hair (horseshoe: sides + back only, bald on top) ------------
        # Left side strip (ear to back of head)
        pygame.draw.rect(surface, hair, (x + 3, y + 8, 3, 11), border_radius=2)
        # Right side strip
        pygame.draw.rect(surface, hair, (x + 22, y + 8, 3, 11), border_radius=2)
        # Receding fringe dots above temples
        pygame.draw.rect(surface, hair, (x + 5, y + 6, 3, 3))
        pygame.draw.rect(surface, hair, (x + 20, y + 6, 3, 3))
        # Faint band around back of head (visible as thin top line at hairline)
        pygame.draw.line(surface, hair, (x + 6, y + 7), (x + 22, y + 7), 1)

        # --- Eyebrows (thin, set well below the hairline) ---------------
        pygame.draw.rect(surface, hair, (x + 7, y + 10, 5, 1))
        pygame.draw.rect(surface, hair, (x + 16, y + 10, 5, 1))

        # --- Round wire glasses ----------------------------------------
        pygame.draw.rect(surface, glass, (x + 7, y + 11, 6, 5), 1, border_radius=3)
        pygame.draw.rect(surface, glass, (x + 15, y + 11, 6, 5), 1, border_radius=3)
        pygame.draw.line(surface, glass, (x + 13, y + 13), (x + 15, y + 13), 1)

        # --- Eyes (small dark pupils behind glasses) --------------------
        pygame.draw.rect(surface, BLACK, (x + 9, y + 13, 2, 2))
        pygame.draw.rect(surface, BLACK, (x + 17, y + 13, 2, 2))

        # --- Nose (subtle vertical shadow) ------------------------------
        pygame.draw.line(surface, skin_shadow, (x + 14, y + 16), (x + 14, y + 18), 1)

        # --- Mouth (neutral line) ---------------------------------------
        pygame.draw.rect(surface, (170, 105, 105), (x + 11, y + 19, 6, 1))

        # --- Body / SSI jacket ------------------------------------------
        pygame.draw.rect(surface, jacket, (x + 4, y + 22, 20, 11), border_radius=3)
        # Shirt V-collar
        pygame.draw.polygon(surface, WHITE,
                            [(x + 10, y + 22), (x + 14, y + 26), (x + 18, y + 22)])
        pygame.draw.line(surface, (30, 40, 60), (x + 14, y + 26), (x + 14, y + 32), 1)

        # --- Hands --------------------------------------------------------
        if self.facing > 0:
            pygame.draw.rect(surface, skin, (x + 20, y + 25, 5, 4), border_radius=2)
        else:
            pygame.draw.rect(surface, skin, (x + 3, y + 25, 5, 4), border_radius=2)

        # --- Legs (dark trousers) ---------------------------------------
        pygame.draw.rect(surface, (38, 46, 72), (x + 7, y + 32, 5, 4), border_radius=1)
        pygame.draw.rect(surface, (38, 46, 72), (x + 16, y + 32, 5, 4), border_radius=1)

        # Fire-state flame tuft on shoulder
        if self.power == "fire":
            flame_flicker = (now // 80) % 2
            fx = x + 22 if self.facing > 0 else x + 6
            pygame.draw.circle(surface, ORANGE, (fx, y + 20 - flame_flicker), 3)
            pygame.draw.circle(surface, YELLOW, (fx, y + 19 - flame_flicker), 2)

        # Label
        label = "ILYA"
        if self.power == "super":
            label = "SUPER ILYA"
        elif self.power == "fire":
            label = "FIRE ILYA"
        if self.starred():
            label = "STAR ILYA"
        draw_label(surface, label, x + PLAYER_WIDTH // 2, y - 12, tint or CYAN, font)

        for fb in self.fireballs:
            fb.draw(surface, camera_x, camera_y)


# ---------------------------------------------------------------------------
# Level
# ---------------------------------------------------------------------------
class Level:
    def __init__(self, definition):
        self.definition = definition
        self.name = definition["name"]
        self.subtitle = definition["subtitle"]
        self.bg_top = definition["bg_top"]
        self.bg_bottom = definition["bg_bottom"]
        self.accent = definition["accent"]
        self.grid_color = definition["grid"]
        self.block_color = definition["block"]
        self.block_top_color = definition["block_top"]
        self.portal_color = definition["portal"]
        self.badge_color = definition["badge"]
        self.required_badges = definition["required_badges"]
        self.rows = definition["rows"]
        self.signs = definition["signs"]
        self.height = len(self.rows)
        self.width = max(len(row) for row in self.rows)
        self.rows = [row.ljust(self.width, ".") for row in self.rows]
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        self.solids = []
        self.hazards = []
        self.collectibles = []
        self.enemies = []
        self.moving_platforms = []
        self.coins = []
        self.question_blocks = []
        self.bricks = []
        self.pipes = []
        self.power_ups = []  # spawned on-demand from question blocks
        self.flagpole = None
        self.portal = None
        self.spawn = (80, 320)
        self.total_badges = 0
        self._parse()

    def _parse(self):
        d = self.definition
        enemy_palettes = {
            "walker": {"body": self.accent, "eye": WHITE},
            "hopper": {"body": self.badge_color, "eye": BLACK},
            "drone": {"body": CYAN, "eye": self.accent},
        }
        question_rewards = d.get("question_rewards", {})
        pending_pipes = {}  # track pipe tops to extend downward
        for row_idx, row in enumerate(self.rows):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if char == "#":
                    self.solids.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == "P":
                    self.spawn = (x + 6, y + 2)
                elif char == "E":
                    self.portal = Portal(x, y + TILE_SIZE, self.portal_color)
                elif char == "c":
                    self.collectibles.append(Collectible(x, y, self.badge_color, d.get("collectible_label", "BADGE")))
                elif char == "!":
                    self.hazards.append(Hazard(x, y, RED, d.get("hazard_label", "SPIKE")))
                elif char == "w":
                    self.enemies.append(WalkerEnemy(x, y, enemy_palettes["walker"], 2.0, d.get("walker_label", "BLOCKER")))
                elif char == "h":
                    self.enemies.append(HopperEnemy(x, y, enemy_palettes["hopper"], d.get("hopper_label", "HOPPER")))
                elif char == "d":
                    self.enemies.append(DroneEnemy(x, y, enemy_palettes["drone"], d.get("drone_label", "DRONE")))
                elif char == "M":
                    self.moving_platforms.append(MovingPlatform(x, y + 10, "x", self.accent))
                elif char == "V":
                    self.moving_platforms.append(MovingPlatform(x, y + 10, "y", self.accent))
                elif char == "?":
                    reward = question_rewards.get((col_idx, row_idx), "coin")
                    self.question_blocks.append(QuestionBlock(x, y, reward))
                elif char == "b":
                    self.bricks.append(Brick(x, y))
                elif char == "o":
                    self.coins.append(Coin(x, y))
                elif char == "F":
                    self.flagpole = Flagpole(x, y + TILE_SIZE)
                elif char == "T":
                    pending_pipes[col_idx] = (x, y, 1)
                elif char == "t":
                    if col_idx in pending_pipes:
                        px, py, ph = pending_pipes[col_idx]
                        pending_pipes[col_idx] = (px, py, ph + 1)
                # AI safety enemies
                elif char == "B":
                    self.enemies.append(BossEnemy(x, y))
                elif char == "g":
                    self.enemies.append(ShadyGregEnemy(x, y))
                elif char == "a":
                    self.enemies.append(EAccZealot(x, y))
                elif char == "$":
                    self.enemies.append(MoneyBagEnemy(x, y))
                elif char == "x":
                    self.enemies.append(CCPSpyDrone(x, y))
        # Build pipes (2-tile-wide); only keep the leftmost of each pair
        consumed = set()
        for col_idx in sorted(pending_pipes.keys()):
            if col_idx in consumed:
                continue
            px, py, ph = pending_pipes[col_idx]
            right = pending_pipes.get(col_idx + 1)
            if right and right[0] == px + TILE_SIZE:
                self.pipes.append(Pipe(px, py, ph))
                consumed.add(col_idx + 1)
        self.total_badges = len(self.collectibles)
        if not self.portal:
            self.portal = Portal((self.width - 2) * TILE_SIZE, (self.height - 2) * TILE_SIZE, self.portal_color)

    def update(self, player_x=None):
        for collectible in self.collectibles:
            collectible.update()
        for coin in self.coins:
            coin.update()
        for qb in self.question_blocks:
            qb.update()
        for brick in self.bricks:
            brick.update()
        for platform in self.moving_platforms:
            platform.update()
        for pu in self.power_ups:
            pu.update(self)
        self.power_ups = [p for p in self.power_ups if p.alive]
        for enemy in self.enemies:
            if isinstance(enemy, (EAccZealot, CCPSpyDrone)):
                enemy.update(self, player_x=player_x)
            else:
                enemy.update(self)

    def draw_background(self, surface, camera_x):
        for y in range(SCREEN_HEIGHT):
            blend = y / SCREEN_HEIGHT
            color = (
                int(lerp(self.bg_top[0], self.bg_bottom[0], blend)),
                int(lerp(self.bg_top[1], self.bg_bottom[1], blend)),
                int(lerp(self.bg_top[2], self.bg_bottom[2], blend)),
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        horizon = SCREEN_HEIGHT * 0.67
        grid_offset = int(camera_x * 0.25) % 80
        for x in range(-grid_offset, SCREEN_WIDTH + 80, 80):
            pygame.draw.line(surface, self.grid_color, (x, horizon), (SCREEN_WIDTH // 2 + (x - SCREEN_WIDTH // 2) * 2, SCREEN_HEIGHT), 1)
        for index in range(12):
            y_pos = horizon + index * 20
            pygame.draw.line(surface, self.grid_color, (0, y_pos), (SCREEN_WIDTH, y_pos), 1)
        for index in range(28):
            star_x = int((index * 173 + camera_x * 0.18) % (SCREEN_WIDTH + 120)) - 40
            star_y = (index * 41) % int(horizon - 24)
            size = 2 if index % 5 == 0 else 1
            surface.fill(WHITE, (star_x, star_y, size, size))

    def draw_world(self, surface, camera_x, camera_y, sign_font, label_font, title_font):
        self.draw_background(surface, camera_x)
        for tile in self.solids:
            x = tile.x - camera_x
            y = tile.y - camera_y
            pygame.draw.rect(surface, self.block_color, (x, y, tile.w, tile.h), border_radius=4)
            pygame.draw.rect(surface, self.block_top_color, (x, y, tile.w, 8), border_radius=4)
            pygame.draw.rect(surface, BLACK, (x + 4, y + 14, tile.w - 8, 3), border_radius=2)
        for pipe in self.pipes:
            pipe.draw(surface, camera_x, camera_y)
        for brick in self.bricks:
            brick.draw(surface, camera_x, camera_y)
        for qb in self.question_blocks:
            qb.draw(surface, camera_x, camera_y, title_font)
        for sign_x, sign_y, text in self.signs:
            x = sign_x - camera_x
            y = sign_y - camera_y
            pygame.draw.rect(surface, BLACK, (x, y, 200, 36), border_radius=4)
            pygame.draw.rect(surface, self.accent, (x, y, 200, 36), 2, border_radius=4)
            surface.blit(sign_font.render(text, True, self.accent), (x + 10, y + 8))
        for platform in self.moving_platforms:
            platform.draw(surface, camera_x, camera_y)
        for hazard in self.hazards:
            hazard.draw(surface, camera_x, camera_y, label_font)
        for coin in self.coins:
            coin.draw(surface, camera_x, camera_y)
        for collectible in self.collectibles:
            collectible.draw(surface, camera_x, camera_y, label_font)
        for pu in self.power_ups:
            pu.draw(surface, camera_x, camera_y, label_font)
        for enemy in self.enemies:
            enemy.draw(surface, camera_x, camera_y, label_font)
        if self.flagpole:
            self.flagpole.draw(surface, camera_x, camera_y)

    def blocking_rects(self):
        rects = list(self.solids)
        rects.extend(platform.rect for platform in self.moving_platforms)
        rects.extend(qb.rect for qb in self.question_blocks)
        rects.extend(brick.rect for brick in self.bricks if not brick.broken)
        rects.extend(pipe.rect for pipe in self.pipes)
        return rects

    def ground_at(self, x, y):
        probe = pygame.Rect(x, y, 4, 4)
        for tile in self.blocking_rects():
            if probe.colliderect(tile):
                return True
        return False


# ---------------------------------------------------------------------------
# Main Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Alignment Adventure 1987 - feat. ILYA vs SCAMA")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("consolas", 42, bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)
        self.label_font = pygame.font.SysFont("consolas", 11, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 52, bold=True)
        self.scanlines = self.build_scanlines()
        # Audio: show a brief loading screen while we synthesize
        self._show_loading()
        self.audio = Audio()
        self.audio.init()
        self.state = "menu"
        self.level_index = 0
        self.level = None
        self.player = None
        self.camera_x = 0
        self.camera_y = 0
        self.banner_until = 0
        self._menu_music_started = False
        self._end_music_played = False

    def _show_loading(self):
        self.screen.fill(BLACK)
        txt = self.title_font.render("GENERATING CHIPTUNE...", True, CYAN)
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        sub = self.small_font.render("(the 1987 synthesizer is warming up)", True, MAGENTA)
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        pygame.display.flip()

    def build_scanlines(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(overlay, (0, 0, 0, 45), (0, y), (SCREEN_WIDTH, y))
        return overlay

    def start_new_game(self):
        self.level_index = 0
        self.load_level(reset_hearts=True)
        self.state = "playing"
        self._end_music_played = False
        self.audio.play_music(f"level{self.level_index + 1}")

    def load_level(self, reset_hearts=False):
        self.level = Level(LEVEL_DEFS[self.level_index])
        if reset_hearts or not self.player:
            self.player = Player(self.level.spawn)
        else:
            self.player.reset_position(self.level.spawn)
            self.player.badges = 0
            self.player.fireballs = []
            self.player.reached_flag = False
        self.player.audio = self.audio
        self.camera_x = 0
        self.camera_y = 0
        self.banner_until = pygame.time.get_ticks() + 2200

    def next_level(self):
        self.level_index += 1
        self.player.hearts = min(Player.HEART_CAP, self.player.hearts + LEVEL_CLEAR_HEAL)
        if self.audio:
            self.audio.play_sfx("portal")
        if self.level_index >= len(LEVEL_DEFS):
            self.state = "win"
            return
        self.load_level(reset_hearts=False)
        self.audio.play_music(f"level{self.level_index + 1}")

    def restart_from_menu(self):
        self.state = "menu"
        self._menu_music_started = False
        self._end_music_played = False
        self.audio.stop_music()

    def update_camera(self):
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        self.camera_x = clamp(int(target_x), 0, max(0, self.level.pixel_width - SCREEN_WIDTH))
        self.camera_y = clamp(int(target_y), 0, max(0, self.level.pixel_height - SCREEN_HEIGHT))

    def get_enemy_rect(self, enemy):
        """Get the effective collision rect for an enemy."""
        if isinstance(enemy, ShadyGregEnemy):
            return enemy.effective_rect
        return enemy.rect

    def update_playing(self):
        keys = pygame.key.get_pressed()
        if pygame.time.get_ticks() >= self.banner_until:
            self.player.update(self.level, keys)
        self.level.update(player_x=self.player.rect.x)
        now = pygame.time.get_ticks()

        # Head-bumps on question blocks / bricks
        if self.player.bumped_block:
            bumped = self.player.bumped_block
            for qb in self.level.question_blocks:
                if qb.rect is bumped:
                    if not qb.spent:
                        reward = qb.bump()
                        self.audio.play_sfx("bump")
                        if reward == "coin":
                            self.player.pickup("coin")
                            self.player.message = "+20 COIN"
                            self.player.message_until = now + 700
                        elif reward:
                            self.level.power_ups.append(
                                PowerUp(qb.rect.x, qb.rect.y, reward)
                            )
                    else:
                        self.audio.play_sfx("bump")
                    break
            for brick in self.level.bricks:
                if brick.rect is bumped and not brick.broken:
                    can_break = self.player.power in ("super", "fire")
                    broken = brick.bump(can_break)
                    if broken:
                        self.player.score += 50
                        self.player.message = "+50 BRICK SMASHED"
                        self.player.message_until = now + 700
                        self.audio.play_sfx("brick")
                    else:
                        self.audio.play_sfx("bump")
                    break

        # Coin pickups
        for coin in self.level.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.pickup("coin")

        # Power-up pickups
        for pu in self.level.power_ups:
            if pu.alive and self.player.rect.colliderect(pu.rect):
                self.player.pickup(pu.kind)
                pu.alive = False

        # Badge collectibles
        for collectible in self.level.collectibles:
            if not collectible.collected and self.player.rect.colliderect(collectible.rect):
                collectible.collected = True
                self.player.badges += 1
                self.player.score += 100
                self.player.message = f"+100 {collectible.label}"
                self.player.message_until = now + 900

        # Hazards
        for hazard in self.level.hazards:
            if self.player.rect.colliderect(hazard.rect):
                self.player.damage(hazard.label)

        # Fireball vs enemies
        for fb in list(self.player.fireballs):
            if not fb.alive:
                continue
            for enemy in self.level.enemies:
                if not enemy.alive:
                    continue
                enemy_rect = self.get_enemy_rect(enemy)
                if fb.rect.colliderect(enemy_rect):
                    if isinstance(enemy, BossEnemy):
                        killed = enemy.hit()
                        self.player.score += 200
                        if killed:
                            self.player.score += 1500
                            self.player.message = "+1500 SCAMA DEFEATED!"
                            self.player.message_until = now + 2000
                    else:
                        enemy.alive = False
                        self.player.score += 250
                        self.player.message = f"+250 burned {enemy.label}"
                        self.player.message_until = now + 900
                    fb.alive = False
                    break

        # Player vs enemies
        for enemy in self.level.enemies:
            if not enemy.alive:
                continue
            enemy_rect = self.get_enemy_rect(enemy)
            if not self.player.rect.colliderect(enemy_rect):
                continue
            if self.player.starred():
                if isinstance(enemy, BossEnemy):
                    killed = enemy.hit()
                    self.player.score += 500
                    if killed:
                        self.player.score += 1500
                        self.player.message = "+1500 STAR-KILLED SCAMA!"
                        self.player.message_until = now + 2000
                else:
                    enemy.alive = False
                    self.player.score += 400
                    self.player.message = f"+400 STAR-KILL {enemy.label}"
                    self.player.message_until = now + 900
                continue
            stomp = self.player.vel.y > 0 and self.player.rect.bottom - enemy_rect.top < 20
            if stomp:
                # Snap above the enemy so we don't re-overlap next frame
                self.player.rect.bottom = enemy_rect.top - 1
                if isinstance(enemy, BossEnemy):
                    killed = enemy.hit()
                    self.player.bounce()
                    self.player.invincible_until = max(self.player.invincible_until, now + 300)
                    self.audio.play_sfx("stomp")
                    if killed:
                        self.player.score += 1500
                        self.player.message = "+1500 SCAMA DEFEATED!"
                        self.player.message_until = now + 2000
                    else:
                        self.player.score += 500
                        self.player.message = f"+500 HIT SCAMA ({enemy.hp} LEFT)"
                        self.player.message_until = now + 1200
                else:
                    enemy.alive = False
                    self.player.score += 250
                    self.player.bounce()
                    self.player.message = f"+250 stomped {enemy.label}!"
                    self.player.message_until = now + 1200
                    self.audio.play_sfx("stomp")
            else:
                self.player.damage(enemy.label)

        # Flagpole
        if self.level.flagpole:
            if not self.player.reached_flag and self.player.rect.colliderect(self.level.flagpole.rect):
                self.player.reached_flag = True
                bonus = max(100, 600 - int((self.player.rect.top - self.level.flagpole.top_y) / 2))
                self.player.score += bonus
                self.player.message = f"+{bonus} FLAGPOLE BONUS"
                self.player.message_until = now + 1400
                self.audio.play_sfx("flagpole")
            if self.player.reached_flag:
                self.level.flagpole.slide_flag()

        # Fall-off-world
        if self.player.rect.top > self.level.pixel_height + 50:
            self.player.damage("fell into the existential risk pit")
            self.player.reset_position(self.level.spawn)

        # Portal
        unlocked = self.player.badges >= self.level.required_badges
        if unlocked and self.player.rect.colliderect(self.level.portal.rect):
            self.next_level()
        if self.player.hearts <= 0:
            self.state = "game_over"
        self.update_camera()

    def draw_hud(self):
        badge_text = f"badges {self.player.badges}/{self.level.required_badges}"
        score_text = f"score {self.player.score}"
        coin_text = f"x {self.player.coins:02d}"
        level_text = self.level.name.upper()
        heart_x = 24
        max_hearts = max(3, self.player.hearts)
        for heart in range(max_hearts):
            color = RED if heart < self.player.hearts else (70, 28, 34)
            points = [
                (heart_x + heart * 30 + 10, 26),
                (heart_x + heart * 30 + 18, 16),
                (heart_x + heart * 30 + 26, 26),
                (heart_x + heart * 30 + 18, 40),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.circle(self.screen, color, (heart_x + heart * 30 + 12, 20), 6)
            pygame.draw.circle(self.screen, color, (heart_x + heart * 30 + 24, 20), 6)
        self.screen.blit(self.ui_font.render(level_text, True, self.level.accent), (24, 54))
        self.screen.blit(self.ui_font.render(badge_text, True, WHITE), (24, 84))
        self.screen.blit(self.ui_font.render(score_text, True, WHITE), (24, 112))
        # Coins icon + count
        pygame.draw.ellipse(self.screen, GOLD, (24, 144, 18, 18))
        pygame.draw.line(self.screen, (140, 100, 0), (33, 146), (33, 160), 2)
        self.screen.blit(self.ui_font.render(coin_text, True, GOLD), (50, 144))
        # Power state pill
        power_colors = {"small": (140, 160, 200), "super": GREEN, "fire": (255, 140, 60)}
        power_labels = {"small": "SMALL", "super": "SUPER", "fire": "FIRE"}
        pc = power_colors[self.player.power]
        pygame.draw.rect(self.screen, pc, (24, 176, 110, 22), border_radius=6)
        pygame.draw.rect(self.screen, BLACK, (24, 176, 110, 22), 2, border_radius=6)
        self.screen.blit(self.small_font.render(power_labels[self.player.power], True, BLACK), (46, 180))
        # Star indicator
        if self.player.starred():
            remaining = max(0, self.player.star_until - pygame.time.get_ticks()) // 100
            self.screen.blit(self.small_font.render(f"STAR {remaining/10:.1f}s", True, YELLOW), (140, 180))
        # Message line
        if pygame.time.get_ticks() < self.player.message_until:
            message_surf = self.ui_font.render(self.player.message.upper(), True, YELLOW)
            self.screen.blit(message_surf, (24, 208))
        # Portal reminder
        if self.player.badges < self.level.required_badges:
            reminder = f"collect {self.level.required_badges - self.player.badges} more badge(s)"
            self.screen.blit(self.small_font.render(reminder, True, self.level.badge_color), (SCREEN_WIDTH - 260, 22))
        else:
            self.screen.blit(self.small_font.render("PORTAL UNLOCKED - GO!", True, self.level.portal_color), (SCREEN_WIDTH - 240, 22))

    def draw_banner(self):
        if pygame.time.get_ticks() >= self.banner_until:
            return
        text = self.title_font.render(self.level.name.upper(), True, self.level.accent)
        sub = self.small_font.render(self.level.subtitle, True, WHITE)
        box = pygame.Rect(100, 150, SCREEN_WIDTH - 200, 130)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), box, border_radius=8)
        pygame.draw.rect(self.screen, self.level.accent, box, 2, border_radius=8)
        self.screen.blit(text, (box.x + 28, box.y + 20))
        self.screen.blit(sub, (box.x + 28, box.y + 68))
        # Level-specific flavor text
        flavors = {
            0: "2015. You are ILYA. Collect arxiv papers. The nonprofit dream is alive.",
            1: "2023. The board fires Sam. Greg vanishes. Survive the chaos.",
            2: "2024. SCAMA returns. You found SSI. e/acc zealots and CCP spies await.",
        }
        flavor = flavors.get(self.level_index, "")
        self.screen.blit(self.small_font.render(flavor, True, YELLOW), (box.x + 28, box.y + 96))

    def draw_menu(self):
        self.screen.fill(BLACK)
        temp_level = Level(LEVEL_DEFS[0])
        temp_level.draw_background(self.screen, 0)
        title = self.big_font.render("ALIGNMENT ADVENTURE", True, CYAN)
        sub = self.title_font.render("ILYA vs SCAMA  -  SSI EDITION", True, MAGENTA)
        self.screen.blit(title, (60, 60))
        self.screen.blit(sub, (200, 120))
        lines = [
            "You are ILYA SUTSKEVER. From early OpenAI to the board coup to SSI.",
            "Survive the blip. Battle SCAMA ALTMAN. Dodge Shady Greg.",
            "Stomp trolls, MSFT lawyers, e/acc zealots, and CCP spy drones.",
            "",
            "HIT ? BLOCKS: coins, ALIGNMENT PATCH (heart), SAFETY STAR, RLHF FLOWER.",
            "BREAK BRICKS while SUPER. SLIDE THE FLAGPOLE for a bonus.",
            "",
            "MOVE: Arrows / WASD     JUMP: Space / W     SHOOT: X / J",
            "ENTER to begin. ESC to quit/return to title. M mutes music.",
        ]
        for idx, line in enumerate(lines):
            color = WHITE if idx != 0 else CYAN
            self.screen.blit(self.small_font.render(line, True, color), (86, 180 + idx * 22))
        # Level preview
        level_names = ["1: EARLY OPENAI", "2: THE BLIP", "3: SSI & FUTURE"]
        level_colors = [GREEN, MAGENTA, RED]
        for i, (name, color) in enumerate(zip(level_names, level_colors)):
            self.screen.blit(self.ui_font.render(name, True, color), (86 + i * 280, 400))

        pulse = 180 + int(math.sin(pygame.time.get_ticks() * 0.007) * 70)
        start_color = (pulse, 255, 180)
        self.screen.blit(self.ui_font.render("PRESS ENTER", True, start_color), (386, 460))

    def draw_end_screen(self, win):
        self.screen.fill(BLACK)
        if win:
            color = GREEN
            headline = "ALIGNMENT ACHIEVED!"
            subline = "ILYA saves the world. SSI ships safe superintelligence."
            flavor = "Eliezer nods. Anthropic claps. SCAMA defeated. The board was right."
        else:
            color = RED
            headline = "MISALIGNMENT WINS"
            subline = "SCAMA ALTMAN ships AGI with zero evals."
            flavor = "Greg reappears. The paperclips multiply. Ilya's regret deepens."
        self.screen.blit(self.big_font.render(headline, True, color), (120, 130))
        self.screen.blit(self.title_font.render(subline, True, WHITE), (120, 210))
        self.screen.blit(self.small_font.render(flavor, True, YELLOW), (120, 270))
        self.screen.blit(self.ui_font.render(f"final score {self.player.score}", True, YELLOW), (360, 320))
        self.screen.blit(self.small_font.render("Press R to retry or Esc for the title screen.", True, WHITE), (280, 380))

    def draw_playing(self):
        self.level.draw_world(self.screen, self.camera_x, self.camera_y, self.small_font, self.label_font, self.ui_font)
        unlocked = self.player.badges >= self.level.required_badges
        self.level.portal.draw(self.screen, self.camera_x, self.camera_y, unlocked)
        self.player.draw(self.screen, self.camera_x, self.camera_y, self.label_font)
        self.draw_hud()
        self.draw_banner()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.restart_from_menu()
                        else:
                            pygame.quit()
                            sys.exit()
                    if event.key == pygame.K_m:
                        enabled = self.audio.toggle_mute()
                        if enabled:
                            # Replay whatever should be playing for the current state
                            self._apply_state_music(force=True)
                    if self.state == "menu" and event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif self.state in {"game_over", "win"} and event.key == pygame.K_r:
                        self.start_new_game()

            # Ensure the right music is playing for the current state
            self._apply_state_music()

            if self.state == "playing":
                self.update_playing()
                self.draw_playing()
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "game_over":
                self.draw_end_screen(False)
            elif self.state == "win":
                self.draw_end_screen(True)

            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()

    def _apply_state_music(self, force=False):
        """Keep music aligned with current game state."""
        if not self.audio or not self.audio.enabled:
            return
        if self.state == "menu":
            if force or not self._menu_music_started:
                self.audio.play_music("menu")
                self._menu_music_started = True
                self._end_music_played = False
        elif self.state == "playing":
            # level-specific; start_new_game / next_level already kicks it off,
            # but on fast-state transitions this keeps it correct
            self.audio.play_music(f"level{self.level_index + 1}")
            self._end_music_played = False
        elif self.state in ("game_over", "win"):
            if not self._end_music_played or force:
                self.audio.stop_music()
                self.audio.play_music("win" if self.state == "win" else "lose", loops=0)
                self._end_music_played = True
                self._menu_music_started = False


if __name__ == "__main__":
    Game().run()
