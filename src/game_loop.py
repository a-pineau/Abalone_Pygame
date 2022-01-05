import os
# Manually places the window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
import math
import pygame
from abalone import Abalone
from constants import *

pygame.init()
screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
pygame.display.set_caption("Abalone")
game = Abalone()

# Game loop
def main():
    running = True
    moving = False
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
            # Selecting a single marble
            elif event.type == MOUSEBUTTONDOWN and not p_keys[K_LSHIFT]:
                for r in game.marbles_rect:
                    if (game.is_inside_marble(event.pos, r.center)
                        and game.marbles_pos[r.topleft] == game.current_color):
                            moving = True
                            game.set_buffers(r.topleft)
                            game.marbles_pos[r.topleft] = MARBLE_FREE
                            break
            # Updating board
            elif event.type == MOUSEBUTTONUP:
                moving = False
                game.apply_buffers()
                game.update_board()
                game.clear_buffers()
            # Moving single marble
            elif event.type == MOUSEMOTION and moving:
                r.move_ip(event.rel)
                game.select_single_marble(event.pos, r)
            # Selecting multiple marbles
            elif p_keys[K_LSHIFT]:
                if not game.buffer_marbles_pos:
                    game.set_buffers()
                if p_mouse[0]:
                    mouse_pos = pygame.mouse.get_pos()
                    for r in game.marbles_rect:
                        if game.is_inside_marble(mouse_pos, r.center):
                            game.select_marbles_range(r)
                            game.compute_new_marbles_range(r)

        game.display_marbles(screen)
        game.display_current_color(screen)
        game.display_time_elapsed(screen)
        game.display_error_message(screen)
        game.draw_circled_line(screen, GREEN_3, 4)
        if moving: 
            screen.blit(game.buffer_color, r)
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()