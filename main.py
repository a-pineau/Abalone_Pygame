"""Implements the game loop and handles the user's events."""

import sys
import os
# Manually places the window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
sys.path.insert(0, "C:/Users/Adrian/Desktop/Python/Abalone_Pygame/src")

import math
import pygame
from abalone import Abalone
from popup_win_game import PopUpWindow
from constants import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QGridLayout, 
                             QWidget, QLayout)
SNAP_FOLDER = os.path.join(os.path.dirname(__file__), "results")
n_snap = 0

# Game loop
def main():
    try:
        os.mkdir(SNAP_FOLDER)
    except FileExistsError:
        print(f"Folder \"{SNAP_FOLDER}\" already exists. Ignoring.")
    if os.path.isdir(SNAP_FOLDER):
        for file_name in os.listdir(SNAP_FOLDER):
            file = os.path.join(SNAP_FOLDER, file_name)
            os.remove(file)
    pygame.init()
    screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
    pygame.display.set_caption("Abalone")
    game = Abalone()
    app = QApplication(sys.argv)
    end_game_popup = PopUpWindow(game)
    running = True
    moving = False
    record = False

    while running:
        # Events handling
        for event in pygame.event.get():
            p_keys = pygame.key.get_pressed()
            p_mouse = pygame.mouse.get_pressed()
            # Quiting game
            if event.type == QUIT:
                running = False
            # Quiting (w/ escape)/Resetting game
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_p:
                    game.reset_game()
                elif event.key == K_F3:
                    record = True if not record else False
            # Selecting a single marble
            elif event.type == MOUSEBUTTONDOWN and not p_keys[K_LSHIFT]:
                for rect in game.marbles_rect:
                    if (game.is_inside_marble(event.pos, rect.center)
                        and game.marbles_pos[rect.topleft] == game.current_color):
                            moving = True
                            game.set_buffers(rect.topleft)
                            game.marbles_pos[rect.topleft] = MARBLE_FREE
                            break
            # Updating board
            elif event.type == MOUSEBUTTONUP:
                moving = False
                game.apply_buffers()
                game.update_board()
                game.clear_buffers()
            # Moving single marble
            elif event.type == MOUSEMOTION and moving:
                rect.move_ip(event.rel)
                game.select_single_marble(event.pos, rect)
            # Selecting multiple marbles
            elif p_keys[K_LSHIFT]:
                if not game.buffer_marbles_pos:
                    game.set_buffers()
                if p_mouse[0]:
                    mouse_pos = pygame.mouse.get_pos()
                    for rect in game.marbles_rect:
                        if game.is_inside_marble(mouse_pos, rect.center):
                            game.select_marbles_range(rect)
                            game.compute_new_marbles_range(rect)

        game.display_marbles(screen)
        game.display_current_color(screen)
        game.display_time_elapsed(screen)
        game.display_error_message(screen)
        game.draw_circled_line(screen, GREEN_3, 4)
        if moving: 
            screen.blit(game.buffer_color, rect)
        game_over = game.check_win_and_display_message(screen)
        if record:
            record_game(screen)
        pygame.display.update()
        if game_over:
            end_game_popup.show()
            running = end_game_popup.get_run_game()
            if not running:
                end_game_popup.close()
            app.setStyle("Fusion")
    pygame.quit()


def record_game(screen) -> None:
    """Save a snapshot of the current grid to the SNAP_FOLDER.

    Parameter
    ---------
    screen: pygame.Surface (required)
        Game window
    """

    global n_snap
    n_snap += 1
    extension = "png"
    file_name = f"snapshot_{n_snap}.{extension}"
    pygame.image.save(screen, os.path.join(SNAP_FOLDER, file_name))


if __name__ == "__main__":
    main()