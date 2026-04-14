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
        "rows": [
            "................................................................................",
            "................................................................................",
            "................................................................................",
            "................................................................................",
            ".....................................................................c..........",
            "..............c.......................c..........................#######......E....",
            ".....P.................c.........########..........c........########.............",
            "###########.......########........................########.........########......",
            "..............c.......................................................c............",
            "...................########......w.....########.........########.................",
            "................................................................................",
            ".......c...................########..............c.........########...............",
            "................................................................................",
            "################################################################################",
        ],
        "signs": [
            (180, 100, "OPENAI EST. 2015"),
            (520, 100, "ELON'S $1B PLEDGE"),
            (900, 100, "ILYA JOINS THE LAB"),
            (1300, 100, "GPT-1 IS BORN"),
            (1700, 100, "SCALING HYPOTHESIS"),
            (2100, 100, "NONPROFIT DREAMS ->"),
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
        "rows": [
            "................................................................................",
            "................................................................................",
            "................................................................................",
            "................................................................................",
            ".....................................................c....................E......",
            "..............c........................c.................########................",
            ".....P.................c.........########.......g................................",
            "###########.......########........................########.........########......",
            "..............c........................................$...........c.............",
            "...................########.............########.........########................",
            "................................................................................",
            ".......c.......g..........########..............c.........########...............",
            "................................................................................",
            "################################################################################",
        ],
        "signs": [
            (180, 100, "NOV 17 2023"),
            (500, 100, "SAM IS FIRED!!"),
            (820, 100, "ILYA: I DEEPLY REGRET"),
            (1200, 100, "GREG GOES DARK"),
            (1550, 100, "700 EMPLOYEES SIGN"),
            (1900, 100, "MICROSOFT CIRCLING"),
            (2250, 100, "SURVIVE THE COUP ->"),
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
        "rows": [
            "................................................................................",
            "................................................................................",
            "................................................................................",
            "................................................................................",
            "......................................................c....................E.....",
            "..............c.......................c.................########......B...........",
            ".....P.................c.........########..........########..........########....",
            "###########.......########........................########........................",
            "..............c.........x..................................a.......c.............",
            "...................########.............########.........########................",
            "................................................................................",
            ".......c...................########..............c..x......########...............",
            "................................................................................",
            "################################################################################",
        ],
        "signs": [
            (180, 100, "ILYA FOUNDS SSI"),
            (520, 100, "SAFE SUPERINTELLIGENCE"),
            (900, 100, "SCAMA ALTMAN RETURNS"),
            (1250, 100, "e/acc VS DOOMERS"),
            (1550, 100, "AGI BY TUESDAY LOL"),
            (1850, 100, "CCP WANTS THE WEIGHTS"),
            (2200, 100, "ALIGNMENT LAB ->"),
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
    """SCAMA ALTMAN - big, fast, menacing."""

    def __init__(self, x, y):
        palette = {"body": (255, 50, 30), "eye": GOLD}
        super().__init__(x, y, palette, "SCAMA ALTMAN")
        self.rect = pygame.Rect(x + 2, y - 6, TILE_SIZE + 4, TILE_SIZE + 6)
        self.start = pygame.Vector2(self.rect.topleft)
        self.vx = 2.8
        self.base_y = self.rect.y

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
        # Bigger red body
        pygame.draw.rect(surface, (180, 20, 10), (x, y, self.rect.w, self.rect.h), border_radius=8)
        # Evil golden eyes
        pygame.draw.rect(surface, GOLD, (x + 6, y + 10, 10, 8), border_radius=2)
        pygame.draw.rect(surface, GOLD, (x + self.rect.w - 16, y + 10, 10, 8), border_radius=2)
        pygame.draw.rect(surface, BLACK, (x + 8, y + 12, 4, 4))
        pygame.draw.rect(surface, BLACK, (x + self.rect.w - 12, y + 12, 4, 4))
        # Evil grin
        pygame.draw.rect(surface, WHITE, (x + 10, y + self.rect.h - 14, self.rect.w - 20, 5), border_radius=2)
        # Dollar signs on body
        dollar_font = font
        dollar_surf = dollar_font.render("$$$", True, GOLD)
        surface.blit(dollar_surf, (x + 8, y + 24))
        # Label
        draw_label(surface, "SCAMA ALTMAN", x + self.rect.w // 2, y - 14, (255, 50, 30), font)


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
    def __init__(self, spawn):
        self.rect = pygame.Rect(spawn[0], spawn[1], PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel = pygame.Vector2()
        self.hearts = 3
        self.invincible_until = 0
        self.on_ground = False
        self.badges = 0
        self.score = 0
        self.facing = 1
        self.message = ""
        self.message_until = 0

    def reset_position(self, spawn):
        self.rect.topleft = spawn
        self.vel.update(0, 0)
        self.on_ground = False

    def damage(self, label):
        now = pygame.time.get_ticks()
        if now < self.invincible_until:
            return False
        self.hearts -= 1
        self.invincible_until = now + INVINCIBLE_MS
        self.message = f"-1 heart: {label}"
        self.message_until = now + 1400
        self.vel.x = -self.facing * 5
        self.vel.y = -6
        return True

    def bounce(self):
        self.vel.y = -9.6

    def update(self, level, keys):
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
                    self.vel.y = 0

        for platform in level.moving_platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y >= 0 and previous_bottom <= platform.rect.top + 8:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.rect.x += int(platform.delta.x)
                    self.rect.y += int(platform.delta.y)

    def draw(self, surface, camera_x, camera_y, font):
        blink = pygame.time.get_ticks() < self.invincible_until and (pygame.time.get_ticks() // 90) % 2 == 0
        if blink:
            return
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y
        # Ilya's white skin face
        pygame.draw.rect(surface, WHITE, (x + 7, y + 7, 14, 18), border_radius=4)
        # Blue jacket (SSI drip)
        pygame.draw.rect(surface, CYAN, (x + 5, y + 22, 18, 11), border_radius=3)
        # Ilya's distinctive dark hair (slightly messy)
        pygame.draw.rect(surface, (50, 35, 25), (x + 4, y - 2, 20, 10), border_radius=4)
        pygame.draw.rect(surface, (50, 35, 25), (x + 3, y + 2, 5, 6), border_radius=2)
        pygame.draw.rect(surface, (50, 35, 25), (x + 20, y + 2, 5, 6), border_radius=2)
        # Face/eyes
        pygame.draw.rect(surface, BLACK, (x + 9, y + 4, 3, 3), border_radius=1)
        pygame.draw.rect(surface, BLACK, (x + 16, y + 4, 3, 3), border_radius=1)
        # Iconic glasses
        pygame.draw.rect(surface, (30, 30, 50), (x + 7, y + 2, 7, 7), 1, border_radius=1)
        pygame.draw.rect(surface, (30, 30, 50), (x + 14, y + 2, 7, 7), 1, border_radius=1)
        pygame.draw.line(surface, (30, 30, 50), (x + 14, y + 5), (x + 14, y + 5), 1)
        # White skin hands
        if self.facing > 0:
            pygame.draw.rect(surface, WHITE, (x + 19, y + 16, 8, 5), border_radius=2)
        else:
            pygame.draw.rect(surface, WHITE, (x + 1, y + 16, 8, 5), border_radius=2)
        # White legs
        pygame.draw.rect(surface, OFF_WHITE, (x + 7, y + 32, 5, 4), border_radius=1)
        pygame.draw.rect(surface, OFF_WHITE, (x + 16, y + 32, 5, 4), border_radius=1)
        # ILYA label
        draw_label(surface, "ILYA", x + PLAYER_WIDTH // 2, y - 12, CYAN, font)


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
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        self.solids = []
        self.hazards = []
        self.collectibles = []
        self.enemies = []
        self.moving_platforms = []
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
                # New AI safety enemies
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
        self.total_badges = len(self.collectibles)
        if not self.portal:
            self.portal = Portal((self.width - 2) * TILE_SIZE, (self.height - 2) * TILE_SIZE, self.portal_color)

    def update(self, player_x=None):
        for collectible in self.collectibles:
            collectible.update()
        for platform in self.moving_platforms:
            platform.update()
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

    def draw_world(self, surface, camera_x, camera_y, sign_font, label_font):
        self.draw_background(surface, camera_x)
        for tile in self.solids:
            x = tile.x - camera_x
            y = tile.y - camera_y
            pygame.draw.rect(surface, self.block_color, (x, y, tile.w, tile.h), border_radius=4)
            pygame.draw.rect(surface, self.block_top_color, (x, y, tile.w, 8), border_radius=4)
            pygame.draw.rect(surface, BLACK, (x + 4, y + 14, tile.w - 8, 3), border_radius=2)
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
        for collectible in self.collectibles:
            collectible.draw(surface, camera_x, camera_y, label_font)
        for enemy in self.enemies:
            enemy.draw(surface, camera_x, camera_y, label_font)

    def blocking_rects(self):
        return self.solids + [platform.rect for platform in self.moving_platforms]

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
        self.state = "menu"
        self.level_index = 0
        self.level = None
        self.player = None
        self.camera_x = 0
        self.camera_y = 0
        self.banner_until = 0

    def build_scanlines(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(overlay, (0, 0, 0, 45), (0, y), (SCREEN_WIDTH, y))
        return overlay

    def start_new_game(self):
        self.level_index = 0
        self.load_level(reset_hearts=True)
        self.state = "playing"

    def load_level(self, reset_hearts=False):
        self.level = Level(LEVEL_DEFS[self.level_index])
        if reset_hearts or not self.player:
            self.player = Player(self.level.spawn)
        else:
            self.player.reset_position(self.level.spawn)
            self.player.badges = 0
        self.camera_x = 0
        self.camera_y = 0
        self.banner_until = pygame.time.get_ticks() + 2200

    def next_level(self):
        self.level_index += 1
        self.player.hearts = min(3, self.player.hearts + LEVEL_CLEAR_HEAL)
        if self.level_index >= len(LEVEL_DEFS):
            self.state = "win"
            return
        self.load_level(reset_hearts=False)

    def restart_from_menu(self):
        self.state = "menu"

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
        unlocked = self.player.badges >= self.level.required_badges
        for collectible in self.level.collectibles:
            if not collectible.collected and self.player.rect.colliderect(collectible.rect):
                collectible.collected = True
                self.player.badges += 1
                self.player.score += 100
                self.player.message = f"+100 {collectible.label}"
                self.player.message_until = pygame.time.get_ticks() + 900
        for hazard in self.level.hazards:
            if self.player.rect.colliderect(hazard.rect):
                self.player.damage(hazard.label)
        for enemy in self.level.enemies:
            if not enemy.alive:
                continue
            enemy_rect = self.get_enemy_rect(enemy)
            if self.player.rect.colliderect(enemy_rect):
                stomp = self.player.vel.y > 0 and self.player.rect.bottom - enemy_rect.top < 18
                if stomp:
                    enemy.alive = False
                    points = 500 if isinstance(enemy, BossEnemy) else 250
                    self.player.score += points
                    self.player.bounce()
                    self.player.message = f"+{points} stomped {enemy.label}!"
                    self.player.message_until = pygame.time.get_ticks() + 1200
                else:
                    self.player.damage(enemy.label)
        if self.player.rect.top > self.level.pixel_height + 50:
            self.player.damage("fell into the existential risk pit")
            self.player.reset_position(self.level.spawn)
        if unlocked and self.player.rect.colliderect(self.level.portal.rect):
            self.next_level()
        if self.player.hearts <= 0:
            self.state = "game_over"
        self.update_camera()

    def draw_hud(self):
        badge_text = f"badges {self.player.badges}/{self.level.required_badges}"
        score_text = f"score {self.player.score}"
        level_text = self.level.name.upper()
        heart_x = 24
        for heart in range(3):
            color = RED if heart < self.player.hearts else (70, 28, 34)
            points = [
                (heart_x + heart * 32 + 10, 26),
                (heart_x + heart * 32 + 18, 16),
                (heart_x + heart * 32 + 26, 26),
                (heart_x + heart * 32 + 18, 40),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.circle(self.screen, color, (heart_x + heart * 32 + 12, 20), 6)
            pygame.draw.circle(self.screen, color, (heart_x + heart * 32 + 24, 20), 6)
        self.screen.blit(self.ui_font.render(level_text, True, self.level.accent), (24, 54))
        self.screen.blit(self.ui_font.render(badge_text, True, WHITE), (24, 84))
        self.screen.blit(self.ui_font.render(score_text, True, WHITE), (24, 112))
        if pygame.time.get_ticks() < self.player.message_until:
            message_surf = self.ui_font.render(self.player.message.upper(), True, YELLOW)
            self.screen.blit(message_surf, (24, 146))
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
        self.screen.blit(title, (60, 80))
        self.screen.blit(sub, (200, 145))
        lines = [
            "You are ILYA SUTSKEVER. From early OpenAI to the board coup to SSI.",
            "Survive the blip. Battle SCAMA ALTMAN. Dodge Shady Greg.",
            "Stomp Twitter trolls, MSFT lawyers, e/acc zealots, and CCP spy drones.",
            "",
            "Collect badges. Stomp blockers. Keep 3 hearts. Save alignment.",
            "WASD / Arrows + SPACE to jump.  ENTER to begin.",
        ]
        for idx, line in enumerate(lines):
            color = WHITE if idx != 0 else CYAN
            self.screen.blit(self.small_font.render(line, True, color), (86, 220 + idx * 28))
        # Level preview
        level_names = ["1: EARLY OPENAI", "2: THE BLIP", "3: SSI & FUTURE"]
        level_colors = [GREEN, MAGENTA, RED]
        for i, (name, color) in enumerate(zip(level_names, level_colors)):
            self.screen.blit(self.ui_font.render(name, True, color), (86 + i * 280, 420))

        pulse = 180 + int(math.sin(pygame.time.get_ticks() * 0.007) * 70)
        start_color = (pulse, 255, 180)
        self.screen.blit(self.ui_font.render("PRESS ENTER", True, start_color), (386, 470))

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
        self.level.draw_world(self.screen, self.camera_x, self.camera_y, self.small_font, self.label_font)
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
                    if self.state == "menu" and event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif self.state in {"game_over", "win"} and event.key == pygame.K_r:
                        self.start_new_game()

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


if __name__ == "__main__":
    Game().run()
