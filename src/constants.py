import os
import pygame
from pygame.locals import *

pygame.init()
useless_screen = pygame.display.set_mode()

SIZE_X, SIZE_Y  = 820, 680
SHIFT_X = SHIFT_Y = 36
FONT = pygame.font.SysFont("Sans", 38)


# Directories
FILE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(FILE_DIR, "../images")
MUSIC_DIR = os.path.join(FILE_DIR, "../music")

# Colors
BACKGROUND = (30, 30, 30)
DEAD_ZONE = (141, 141, 141)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
RED_2 = (207, 46, 46)
BLUE_MARBLE = (158, 190, 228, 255)
YELLOW = (255, 255, 0)
YELLOW_MARBLE = (249, 217, 84, 255)
GREEN = (0, 255, 0)
GREEN_2 = (39, 151, 0)
GREEN_3 = (102, 203, 112)
ARROW_COLOR = (255, 0, 247)

# Images
# https://www.iconshock.com/flat-icons/3d-graphics-icons/sphere-icon/
MARBLE_RED = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_red.png")
    ).convert_alpha()
MARBLE_GREEN = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_green.png")
    ).convert_alpha()
MARBLE_BLUE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_blue.png")
    ).convert_alpha()
DEAD_BLUE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_blue.png")
    ).convert_alpha()
DEAD_BLUE.set_alpha(128)
MARBLE_YELLOW = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_yellow.png")
    ).convert_alpha()
DEAD_YELLOW = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_yellow.png")
    ).convert_alpha()
DEAD_YELLOW.set_alpha(128)
MARBLE_PURPLE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_purple.png")
    ).convert_alpha()
MARBLE_CYAN = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_cyan.png")
    ).convert_alpha()
MARBLE_BROWN = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_brown.png")
    ).convert_alpha()
MARBLE_FREE = pygame.image.load(
    os.path.join(IMAGES_DIR, "sphere_empty.png")
    ).convert_alpha()
# https://icons8.com/icon/54885/skull
SKULL = pygame.image.load(
    os.path.join(IMAGES_DIR, "skull.png")
).convert_alpha()
SKULL = pygame.transform.rotozoom(SKULL, 0, 0.7)  # adjusting size

MARBLE_SIZE = 30
MARBLE_IMGS = {
    1: MARBLE_FREE, 
    2: MARBLE_BLUE, 
    3: MARBLE_YELLOW,
}
MARBLE_DEBUG = {
    MARBLE_FREE: "Free", 
    MARBLE_BLUE: "Blue", 
    MARBLE_YELLOW: "Yellow",
    MARBLE_BROWN: "Brown",
}

# Sounds
SOUND_01 = pygame.mixer.Sound(
    os.path.join(MUSIC_DIR, "01_GROWING_ON_ME.wav"))


# Initial configurations
STANDARD = (
    [2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2],
    [1, 1, 2, 2, 2, 1, 1],
    [1, 1, 1, 2, 2, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 3, 3, 3, 1, 1],
    [3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3],
)
GERMAN_DAISY = (
    [1, 1, 1, 1, 1],
    [2, 2, 1, 1, 3, 3],
    [2, 2, 2, 1, 3, 3, 3],
    [1, 2, 2, 1, 1, 3, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 1, 1, 2, 2, 1],
    [3, 3, 3, 1, 2, 2, 2],
    [3, 3, 1, 1, 2, 2],
    [1, 1, 1, 1, 1],
)
BELGIAN_DAISY = (
    [2, 2, 1, 3, 3],
    [2, 2, 2, 3, 3, 3],
    [1, 2, 2, 1, 3, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 1, 2, 2, 1],
    [3, 3, 3, 2, 2, 2],
    [3, 3, 1, 2, 2],
)
DUTCH_DAISY = (
    [2, 2, 1, 3, 3],
    [2, 3, 2, 3, 2, 3],
    [1, 2, 2, 1, 3, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 1, 2, 2, 1],
    [3, 2, 3, 2, 3, 2],
    [3, 3, 1, 2, 2],
)
SWISS_DAISY = (
    [1, 1, 1, 1, 1],
    [2, 2, 1, 1, 3, 3],
    [2, 3, 2, 1, 3, 2, 3],
    [1, 2, 2, 1, 1, 3, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 1, 1, 2, 2, 1],
    [3, 2, 3, 1, 2, 3, 2],
    [3, 3, 1, 1, 2, 2],
    [1, 1, 1, 1, 1],
)
DOMINATION = (
    [1, 1, 1, 1, 1],
    [2, 1, 1, 1, 1, 3],
    [2, 2, 1, 1, 1, 3, 3],
    [2, 2, 2, 2, 1, 3, 3, 3],
    [1, 1, 1, 3, 1, 3, 1, 1, 1],
    [3, 3, 3, 1, 2, 2, 2, 2],
    [3, 3, 1, 1, 1, 2, 2],
    [3, 1, 1, 1, 1, 2],
    [1, 1, 1, 1, 1],
)
PYRAMID = (
    [2, 1, 1, 1, 1],
    [2, 2, 1, 1, 1, 1],
    [2, 2, 2, 1, 1, 1, 1],
    [2, 2, 2, 2, 1, 1, 1, 1],
    [2, 2, 2, 2, 1, 3, 3, 3, 3],
    [1, 1, 1, 1, 3, 3, 3, 3],
    [1, 1, 1, 1, 3, 3, 3],
    [1, 1, 1, 1, 3, 3],
    [1, 1, 1, 1, 3],
)
THE_WALL = (
    [1, 1, 2, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [3, 3, 3, 3, 3, 3, 3, 3],
    [1, 3, 3, 3, 3, 3, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 3, 1, 1],
)

if __name__ == "__main__":
    pass