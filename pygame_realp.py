from typing import Collection
import pygame
import os

from pygame.locals import *
from game_data import STANDARD
from user_messages import ask_messages, err_messages, info_messages
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
    for row in STANDARD:
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

def is_valid_neighboor(init_pos, target_pos, h_range=False):
    x, y = init_pos
    neighboors = [
        (x - MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y - 2 * MARBLE_SIZE),
        (x - MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        (x + MARBLE_SIZE, y + 2 * MARBLE_SIZE),
    ]
    if not h_range:
        neighboors.extend([(x - 2 * MARBLE_SIZE, y),
                           (x + 2 * MARBLE_SIZE, y)])
    return target_pos in neighboors

def recolor_marbles(marbles_pos, target, reset_list, 
                    reset_color, new_color=None):
    for k, v in marbles_pos.items():
        if v in reset_list:
            marbles_pos[k] = reset_color
    if new_color:
        marbles_pos[target] = new_color

def select_single_marble(mouse_pos, marbles_pos, marbles_rect, 
                         current, init_pos):
    target = None
    for t in marbles_rect:
        target = t.topleft
        if t.collidepoint(mouse_pos) and current != t:
            if (marbles_pos[target] == MARBLE_FREE):
                valid_neighboor = is_valid_neighboor(
                    init_pos, 
                    t.topleft, 
                    False)
                highlight = MARBLE_GREEN if valid_neighboor else MARBLE_RED
                recolor_marbles(
                    marbles_pos, target, 
                    [MARBLE_GREEN, MARBLE_RED], 
                    MARBLE_FREE, 
                    highlight)
                    
# def mark_valid_neighboors(marbles_pos, current):
#     x, y = current
#     neighboors = (
#         (x - MARBLE_SIZE, y - 2 * MARBLE_SIZE),
#         (x + MARBLE_SIZE, y - 2 * MARBLE_SIZE),
#         (x - MARBLE_SIZE, y + 2 * MARBLE_SIZE),
#         (x + MARBLE_SIZE, y + 2 * MARBLE_SIZE),
#         (x - 2 * MARBLE_SIZE, y),
#         (x + 2 * MARBLE_SIZE, y),
#     )
#     for n in neighboors:
#         try:
#             marbles_pos[n] 
#         except KeyError:
#             continue
#         else:
#             if marbles_pos[n] == MARBLE_FREE:
#                 marbles_pos[n] = MARBLE_GREEN

def select_marbles_range(marbles_pos, marbles_rect):
    mouse_pos = pygame.mouse.get_pos()
    for r in marbles_rect:
        if r.collidepoint(mouse_pos): 
            # first color the selected marbles in purple (if possible)
            if marbles_pos[r.topleft] == MARBLE_BLUE:
                marbles_pos[r.topleft] = MARBLE_PURPLE
                marbles_range.add(r.topleft)
                # cannot select more than 3 marbles
                if len(marbles_range) > 3:
                    recolor_marbles(marbles_pos, r.topleft, [MARBLE_PURPLE], 
                                    MARBLE_BLUE)
                    marbles_range.clear()
                    return None
                range_type = check_range_type(marbles_range)
                marbles_pos[r.topleft] = MARBLE_PURPLE

            # then color the new positions in green (if possible)
            elif (marbles_pos[r.topleft] == MARBLE_FREE
                  and len(marbles_range) > 1):
                last_marble = marbles_range[-1]
                if is_valid_neighboor(last_marble, r.topleft, True):
                    new_marbles_range = []
                    r_x = marbles_range[-1][0]
                    l_x = marbles_range[0][0]
                    k = 1 if l_x > r_x else -1

                    for i in range(len(marbles_range)):
                        new_marbles_range.append(
                            (r.topleft[0] + k * 2 * i * MARBLE_SIZE, 
                             r.topleft[1])
                        )
                    valid_range = all(
                        marbles_pos[elem] == MARBLE_FREE
                        for elem in new_marbles_range
                    )
                    if valid_range:
                        for marble in new_marbles_range:
                            recolor_marbles(
                                marbles_pos, marble, 
                                [MARBLE_RED], 
                                MARBLE_FREE, 
                                MARBLE_GREEN)
                else:
                    recolor_marbles(
                        marbles_pos, r.topleft, 
                        [MARBLE_GREEN, MARBLE_RED], 
                        MARBLE_FREE, 
                        MARBLE_RED)

def move_marbles(marbles_pos, old_marbles_range, 
                 new_marbles_range, current_color):
    for old_pos, new_pos in zip(old_marbles_range, new_marbles_range):
        print(old_pos, new_pos)
    
def check_range_type(marbles_range):
    if (len(set(elem[1] for elem in marbles_range)) == 1
        and len(marbles_range) in (2, 3)):
        return "horizontal"
    return False

def display_time_elasped(screen):
    time_elasped = f"Time: {int(pygame.time.get_ticks() / 1e3)} s"
    screen.blit(FONT.render(time_elasped, True, TXT_COLOR), (10, 10))

# --------------------------------------------------------------

marbles_pos, marbles_rect = build_marbles()

# Game loop
running = True
moving = False
marbles_range = OrderedSet()

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
                    init_color = marbles_pos[r.topleft]
                    marbles_pos[r.topleft] = MARBLE_FREE
                    break
        elif event.type == MOUSEBUTTONUP:
            moving = False
            # marbles_pos, marbles_rect = build_marbles()
        elif event.type == MOUSEMOTION and moving:
            r.move_ip(event.rel)
            select_single_marble(event.pos, marbles_pos, 
                                 marbles_rect, r, init_pos)
        elif p_keys[K_LSHIFT]:
                if p_mouse[0]:
                    new_marbles_range = select_marbles_range(
                        marbles_pos, 
                        marbles_rect
                        )
                else:
                    pass
                    # marbles_range.clear()


    display_marbles(screen, marbles_pos)
    if moving:
        screen.blit(init_color, r)

    display_time_elasped(screen)
    pygame.display.update()

pygame.quit()















