import pygame
import os

from pygame.locals import *
from init_configurations import BOARD_STANDARD
from UserMessages import ask_messages, err_messages, info_messages
from ordered_set import OrderedSet

pygame.init()

# --------------------------------------------------------------

SIZE_X, SIZE_Y  = 640, 640
BACKGROUND = (30, 30, 30)
FONT = pygame.font.SysFont("Sans", 35)
TXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
pygame.display.set_caption("Abalone")
clock = pygame.time.Clock()

FILE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(FILE_DIR, "images")

# Free icons: https://www.iconshock.com/flat-icons/3d-graphics-icons/sphere-icon/
MARBLE_RED = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_red.png")
    ).convert_alpha()
MARBLE_GREEN = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_green.png")
    ).convert_alpha()
MARBLE_BLUE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_blue.png")
    ).convert_alpha()
MARBLE_PURPLE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_purple.png")
    ).convert_alpha()
MARBLE_YELLOW = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_yellow.png")
    ).convert_alpha()
MARBLE_FREE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_empty.png")
    ).convert_alpha()

MARBLE_SIZE = 30
MARBLE_IMGS = {1: MARBLE_FREE, 2: MARBLE_BLUE, 3: MARBLE_YELLOW}

# --------------------------------------------------------------

def build_marbles():
    marbles_pos = dict()
    marbles_rect = []

    y_init = SIZE_Y / 2 - 10 * MARBLE_SIZE # hard-coded
    disp_y = MARBLE_SIZE
    for row in BOARD_STANDARD:
        x_init = 290 - len(row) * MARBLE_SIZE # hard-coded
        disp_x = MARBLE_SIZE
        for element in row:
            x = x_init + disp_x
            y = y_init + disp_y
            marbles_pos[(x, y)] = MARBLE_IMGS[element]
            marbles_rect.append(
                MARBLE_IMGS[element].get_rect(topleft = (x, y))
            )
            disp_x += 2 * MARBLE_SIZE
        disp_y += 2 * MARBLE_SIZE  

    return marbles_pos, marbles_rect

def display_marbles(screen, marbles_pos):
    screen.fill(BACKGROUND)
    for key, value in marbles_pos.items():
        screen.blit(value, key)

def is_valid_neighboor(init_pos, target_pos):
    x, y = init_pos
    neighboors = (
        (x - MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x - MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        (x - 2 * MARBLE_SIZE, y),
        (x + 2 * MARBLE_SIZE, y),
    )
    return target_pos in neighboors

def highlight_marbles(event, marbles_pos, 
                      marbles_rect, current):
    for t in marbles_rect:
        if t.collidepoint(event.pos) and r != t:
            if (marbles_pos[t.topleft] == MARBLE_FREE):
                valid_neighboor = is_valid_neighboor(current, t.topleft)
                highlight = MARBLE_GREEN if valid_neighboor else MARBLE_RED
                for k, v in marbles_pos.items():
                    if v in (MARBLE_GREEN, MARBLE_RED):
                        marbles_pos[k] = MARBLE_FREE
                    marbles_pos[t.topleft] = highlight
                    
def mark_valid_neighboors(marbles_pos, current):
    x, y = current
    neighboors = (
        (x - MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x - MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        (x - 2 * MARBLE_SIZE, y),
        (x + 2 * MARBLE_SIZE, y),
    )
    for n in neighboors:
        try:
            marbles_pos[n] 
            if marbles_pos[n] == MARBLE_FREE:
                marbles_pos[n] = MARBLE_GREEN
        except KeyError:
            continue

def select_multiple_marbles(marbles_rect, marbles_pos):
    mouse_pos = pygame.mouse.get_pos()
    for r in marbles_rect:
        if (r.collidepoint(mouse_pos)
            and marbles_pos[r.topleft] not in (MARBLE_FREE, MARBLE_GREEN)):
            marbles_pos[r.topleft] = MARBLE_PURPLE
            multiple_marbles.add(r.topleft)

            # cannot select more than 3 marbles
            if len(multiple_marbles) > 3:
                for k, v in marbles_pos.items():
                    if v == MARBLE_PURPLE:
                        marbles_pos[k] = MARBLE_BLUE
                multiple_marbles.clear()

        elif len(multiple_marbles) > 1:
            target = r.topleft
            last_selection = multiple_marbles[-1]
            if (r.collidepoint(mouse_pos) 
                and marbles_pos[target] == MARBLE_FREE):
                    if is_valid_range(multiple_marbles):
                        if is_valid_neighboor(last_selection, target):
                            if MARBLE_GREEN not in marbles_pos.values():
                                marbles_pos[target] = MARBLE_GREEN


def is_valid_range(multiple_marbles):
    if len(set(elem[1] for elem in multiple_marbles)) == 1:
        return True

def display_time_elasped(screen):
    time_elasped = f"Time: {int(pygame.time.get_ticks() / 1e3)} s"
    screen.blit(FONT.render(time_elasped, True, TXT_COLOR), (10, 10))

# --------------------------------------------------------------

marbles_pos, marbles_rect = build_marbles()

# Game loop
running = True
moving = False
multiple_marbles = OrderedSet()

while running:
    # display the current state 
    for event in pygame.event.get():
        p_keys = pygame.key.get_pressed()
        p_mouse = pygame.mouse.get_pressed()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == MOUSEBUTTONDOWN and not p_keys[K_LSHIFT]:
            for r in marbles_rect:
                if (r.collidepoint(event.pos) 
                    and marbles_pos[r.topleft] != MARBLE_FREE):
                    moving = True
                    init_pos = r.topleft
                    init_color = marbles_pos[init_pos]
                    marbles_pos[init_pos] = MARBLE_FREE
                    break
        elif event.type == MOUSEBUTTONUP:
            moving = False
            marbles_pos, marbles_rect = build_marbles()
        elif event.type == MOUSEMOTION and moving:
            r.move_ip(event.rel)
            highlight_marbles(event, marbles_pos, marbles_rect, init_pos)
        elif p_keys[K_LSHIFT]:
                if p_mouse[0]:
                    select_multiple_marbles(marbles_rect, marbles_pos)
                else:
                    multiple_marbles.clear()


    display_marbles(screen, marbles_pos)
    if moving:
        screen.blit(init_color, r)

    display_time_elasped(screen)
    pygame.display.update()

pygame.quit()















