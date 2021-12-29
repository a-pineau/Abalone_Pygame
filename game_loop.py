import pygame

from pygame.locals import *
from abalone import Abalone
from constants import *

screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
pygame.display.set_caption("Abalone")
clock = pygame.time.Clock()
game = Abalone(screen)

# Game loop
def main():
    running = True
    moving = False

    while running:
        # Events handling
        for event in pygame.event.get():
            p_keys = pygame.key.get_pressed()
            p_mouse = pygame.mouse.get_pressed()
            # Quiting/reseting game
            if event.type == KEYDOWN:
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
                    game.select_marbles_range(mouse_pos)

        game.display_marbles(screen)
        game.display_current_color(screen)
        game.display_time_elasped(screen)
        if moving: screen.blit(game.buffer_color, r)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()