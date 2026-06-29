# ═══════════════════════════════════════════════════════
# GALAXY DEFENDER · SHOWCASE BUILD (local pygame, with sound)
#
# How to run:
#   1. Install Python from https://python.org (3.8 or newer)
#   2. Open a terminal and run:  pip install pygame
#   3. Put this file in the SAME folder as the 5 .mp3 files
#   4. Double-click this file (or:  python galaxy_defender_showcase.py)
#   5. Press SPACE to start, arrows to move, SPACE to shoot
#
# Sounds expected in the same folder as this script:
#   game_intro.mp3   game_start.mp3   game_playing.mp3
#   bullet_fire.mp3  game_over.mp3
# ═══════════════════════════════════════════════════════

import os
import pygame
import random

# Resolve sound paths relative to THIS file so the game runs from
# anywhere (double-click or command line).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

WIDTH, HEIGHT = 800, 600
# Try fullscreen first (looks great for screen recording); fall back to
# a regular window if fullscreen isn't available on this machine.
try:
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
except pygame.error:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Defender · Showcase")
clock = pygame.time.Clock()

# ─── Colours ──────────────────────────────────────────
SPACE  = (5, 5, 25)
WHITE  = (255, 255, 255)
CYAN   = (80, 230, 255)
YELLOW = (255, 215, 0)
RED    = (240, 60, 60)
PURPLE = (200, 80, 200)
ORANGE = (255, 140, 40)

# ─── Sound (silent if a file is missing) ──────────────
def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join(SCRIPT_DIR, name))
    except Exception:
        return None

def play(s, vol=0.7):
    if s:
        s.set_volume(vol)
        s.play()

snd_intro = load_sound("game_intro.mp3")
snd_start = load_sound("game_start.mp3")
snd_fire  = load_sound("bullet_fire.mp3")
snd_over  = load_sound("game_over.mp3")

def start_music():
    try:
        pygame.mixer.music.load(os.path.join(SCRIPT_DIR, "game_playing.mp3"))
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)   # loop forever during play
    except Exception:
        pass

def stop_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

# 🎵 game_intro plays as soon as you run the file
play(snd_intro, vol=0.6)

# ─── Sprite helpers ───────────────────────────────────
def draw_ship(s, x, y):
    pygame.draw.polygon(s, CYAN,
        [(x+30, y), (x+60, y+40), (x+40, y+30), (x+20, y+30), (x, y+40)])
    pygame.draw.circle (s, WHITE, (x+30, y+18), 6)
    pygame.draw.polygon(s, ORANGE, [(x+25, y+30), (x+35, y+30), (x+30, y+45)])
    pygame.draw.polygon(s, YELLOW, [(x+27, y+30), (x+33, y+30), (x+30, y+40)])

def draw_laser(s, b):
    pygame.draw.ellipse(s, ORANGE, (b.x-4, b.y-6, b.width+8, b.height+12))
    pygame.draw.ellipse(s, YELLOW, b)

def draw_invader(s, e):           # red square-foot alien
    x, y = e.x, e.y
    pygame.draw.rect(s, RED,   (x+10, y+5,  30, 25))
    pygame.draw.rect(s, RED,   (x,    y+15, 50, 15))
    pygame.draw.rect(s, RED,   (x+5,  y+30, 8,  10))
    pygame.draw.rect(s, RED,   (x+37, y+30, 8,  10))
    pygame.draw.rect(s, WHITE, (x+16, y+12, 6,  6))
    pygame.draw.rect(s, WHITE, (x+28, y+12, 6,  6))

def draw_saucer(s, e):            # yellow disc alien
    x, y = e.x, e.y
    pygame.draw.ellipse(s, YELLOW, (x,    y+12, 50, 22))
    pygame.draw.ellipse(s, ORANGE, (x+12, y+2,  26, 18))
    pygame.draw.circle (s, RED,    (x+25, y+10), 4)
    for i in range(5):
        pygame.draw.circle(s, ORANGE, (x+5 + i*10, y+22), 2)

def draw_crab(s, e):              # purple crab alien
    x, y = e.x, e.y
    pygame.draw.ellipse(s, PURPLE, (x+5, y+10, 40, 25))
    pygame.draw.circle (s, WHITE,  (x+15, y+18), 4)
    pygame.draw.circle (s, WHITE,  (x+35, y+18), 4)
    pygame.draw.circle (s, (0,0,0),(x+15, y+18), 2)
    pygame.draw.circle (s, (0,0,0),(x+35, y+18), 2)
    pygame.draw.line   (s, PURPLE, (x+8,  y+8), (x+2,  y),  3)
    pygame.draw.line   (s, PURPLE, (x+42, y+8), (x+48, y),  3)
    for dx in (5, 15, 25, 35, 45):
        pygame.draw.line(s, PURPLE, (x+dx, y+33), (x+dx, y+42), 2)

ALIEN_DRAWERS = [draw_invader, draw_saucer, draw_crab]

# ─── Load the 3 enemy ship images (ship1.jpg / ship2.jpg / ship 3.jpg) ──
# Files must sit in the SAME folder as this script. They're flipped 180°
# so they face down toward the player (since enemies fly DOWN at you).
# Backgrounds use a colour-key on the top-left pixel to fake transparency
# — works well if your ship images sit on a flat dark/solid background.
ENEMY_SIZE = (60, 50)   # a touch bigger than the 50x40 hitbox so ships pop
ENEMY_SHIPS = []
SHIP_FILES = ["ship1.jpg", "ship2.jpg", "ship 3.jpg"]

for fname in SHIP_FILES:
    path = os.path.join(SCRIPT_DIR, fname)
    try:
        img = pygame.image.load(path).convert()
        # Use the very top-left pixel as the "background" colour to hide
        img.set_colorkey(img.get_at((0, 0)))
        # Scale to enemy size
        img = pygame.transform.smoothscale(img, ENEMY_SIZE)
        # Rotate 180° so the ship points DOWN at the player
        img = pygame.transform.rotate(img, 180)
        ENEMY_SHIPS.append(img)
    except Exception as e:
        print(f"⚠️  Could not load {fname}: {e}")
        ENEMY_SHIPS.append(None)

def draw_enemy(s, e, kind):
    """Blit the ship image if loaded, else fall back to the drawn alien."""
    img = ENEMY_SHIPS[kind] if kind < len(ENEMY_SHIPS) else None
    if img is not None:
        # Centre the bigger sprite on the smaller hitbox so collisions still match
        offset_x = (ENEMY_SIZE[0] - 50) // 2
        offset_y = (ENEMY_SIZE[1] - 40) // 2
        s.blit(img, (e.x - offset_x, e.y - offset_y))
    else:
        ALIEN_DRAWERS[kind](s, e)

# ─── Starfield ────────────────────────────────────────
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
          random.randint(1, 2), random.choice([1, 1, 2, 3])]
         for _ in range(100)]
def update_stars():
    for st in stars:
        st[1] += st[3]
        if st[1] > HEIGHT:
            st[0], st[1] = random.randint(0, WIDTH), 0

def draw_stars(s):
    for sx, sy, sz, _ in stars:
        pygame.draw.circle(s, WHITE, (sx, sy), sz)

# ─── Game state ───────────────────────────────────────
font     = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 64, bold=True)

def draw_text(text, x, y, color=WHITE, big=False, centre=False):
    f = big_font if big else font
    img = f.render(text, True, color)
    if centre:
        x -= img.get_width() // 2
    screen.blit(img, (x, y))

player = pygame.Rect(370, 500, 60, 40)
bullets, enemies, kinds = [], [], []
score, lives, level = 0, 3, 1
state = "MENU"
TARGET = 30

def spawn_enemy():
    enemies.append(pygame.Rect(random.randint(0, WIDTH - 50),
                               random.randint(-300, -50), 50, 40))
    kinds.append(random.randint(0, 2))

def reset_game():
    global score, lives, level, state, bullets, enemies, kinds
    score, lives, level = 0, 3, 1
    bullets, enemies, kinds = [], [], []
    player.x, player.y = 370, 500
    for _ in range(5):
        spawn_enemy()
    state = "PLAYING"

for _ in range(5):
    spawn_enemy()

# ─── Game loop ────────────────────────────────────────
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:        # ESC quits the game
                running = False
            if event.key == pygame.K_F11:           # F11 toggles fullscreen
                pygame.display.toggle_fullscreen()
            if state == "MENU" and event.key == pygame.K_SPACE:
                play(snd_start)
                start_music()
                reset_game()
            elif state == "PLAYING" and event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.x + 27, player.y, 6, 18))
                play(snd_fire, vol=0.5)
            elif state in ("GAME_OVER", "WIN") and event.key == pygame.K_r:
                play(snd_start)
                start_music()
                reset_game()

    keys = pygame.key.get_pressed()
    update_stars()
    screen.fill(SPACE)
    draw_stars(screen)

    if state == "MENU":
        draw_text("GALAXY DEFENDER", WIDTH//2, 180, color=YELLOW, big=True, centre=True)
        draw_text("Arrow keys to move · SPACE to shoot", WIDTH//2, 280, centre=True)
        draw_text("First to " + str(TARGET) + " wins!", WIDTH//2, 320, color=CYAN, centre=True)
        draw_text("Press SPACE to start", WIDTH//2, 400, color=YELLOW, centre=True)

    elif state == "PLAYING":
        speed = 5 + level
        if keys[pygame.K_LEFT]  and player.x > 0:           player.x -= speed
        if keys[pygame.K_RIGHT] and player.x < WIDTH - 60:  player.x += speed
        if keys[pygame.K_UP]    and player.y > 0:           player.y -= speed
        if keys[pygame.K_DOWN]  and player.y < HEIGHT - 40: player.y += speed

        for b in bullets[:]:
            b.y -= 12
            if b.y < 0:
                bullets.remove(b)

        enemy_speed = 2 + level
        for i, e in enumerate(enemies):
            e.y += enemy_speed
            if e.y > HEIGHT:
                e.y = random.randint(-200, -50)
                e.x = random.randint(0, WIDTH - 50)
                lives -= 1
                if lives <= 0:
                    state = "GAME_OVER"
                    stop_music()
                    play(snd_over)
            if player.colliderect(e):
                state = "GAME_OVER"
                stop_music()
                play(snd_over)

        for b in bullets[:]:
            for i, e in enumerate(enemies):
                if b.colliderect(e):
                    if b in bullets:
                        bullets.remove(b)
                    e.y = random.randint(-200, -50)
                    e.x = random.randint(0, WIDTH - 50)
                    kinds[i] = random.randint(0, 2)
                    score += 1
                    if score == TARGET:
                        state = "WIN"
                        stop_music()
                    if score % 10 == 0:
                        level += 1
                        spawn_enemy()

        draw_ship(screen, player.x, player.y)
        for b in bullets:
            draw_laser(screen, b)
        for i, e in enumerate(enemies):
            draw_enemy(screen, e, kinds[i])

        draw_text("Score: " + str(score) + " / " + str(TARGET), 10, 10)
        draw_text("Lives: " + str(lives), WIDTH - 130, 10, color=RED)
        draw_text("Level: " + str(level), WIDTH//2 - 50, 10, color=CYAN)

    elif state == "WIN":
        draw_text("MISSION COMPLETE!", WIDTH//2, 220, color=YELLOW, big=True, centre=True)
        draw_text("You saved the galaxy.", WIDTH//2, 310, color=CYAN, centre=True)
        draw_text("Press R to play again", WIDTH//2, 360, centre=True)

    elif state == "GAME_OVER":
        draw_text("GAME OVER", WIDTH//2, 220, color=RED, big=True, centre=True)
        draw_text("Final score: " + str(score), WIDTH//2, 310, color=YELLOW, centre=True)
        draw_text("Press R to try again", WIDTH//2, 360, centre=True)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
