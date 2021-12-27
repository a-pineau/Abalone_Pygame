import pygame
import math
import random

from pygame.locals import *
from constants import *
from user_messages import ask_messages, err_messages, info_messages
from ordered_set import OrderedSet
from copy import deepcopy

pygame.init()

# --------------------------------------------------------------



FONT = pygame.font.SysFont("Sans", 35)
screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
pygame.display.set_caption("Abalone")
clock = pygame.time.Clock()

# --------------------------------------------------------------

class Abalone(pygame.sprite.Sprite):
    """
    TODO
    """
    def __init__(self, screen, configuration=STANDARD):
        """
        TODO
        """
        super().__init__()
        self.marbles_pos = dict()
        self.marbles_rect = []
        self.build_marbles()

        self.marbles_range = OrderedSet()
        self.new_marbles_range = dict()
        self.buffer_marble = None
        self.buffer_color = None
        self.buffer_marbles_pos = dict()
        self.buffer_marbles_rect = []
        self.tagged_solid_neighboors = []
        self.current_color = random.choice((MARBLE_BLUE, MARBLE_YELLOW))

    def build_marbles(self):
        """
        TODO
        """
        y_init = SIZE_Y / 2 - 10 * MARBLE_SIZE # hard-coded (to change)
        gap_y = MARBLE_SIZE
        for row in STANDARD:
            x_init = 290 - len(row) * MARBLE_SIZE # hard-coded (to change)
            gap_x = MARBLE_SIZE
            for element in row:
                x = x_init + gap_x
                y = y_init + gap_y
                self.marbles_pos[(x, y)] = MARBLE_IMGS[element]
                self.marbles_rect.append(
                    MARBLE_IMGS[element].get_rect(topleft = (x, y))
                )
                gap_x += 2 * MARBLE_SIZE
            gap_y += 2 * MARBLE_SIZE  
    

    def display_marbles(self, screen):
        """
        TODO
        """
        screen.fill(BACKGROUND)
        for key, value in self.marbles_pos.items():
            screen.blit(value, key)

    def is_valid_neighboor(self, target_pos, h_range=False) -> bool:
        """
        TODO
        """
        x, y = self.buffer_marble
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

    def recolor_marbles(self, target, reset_list, 
                        reset_color, new_color=None) -> None:
        """
        TODO
        """
        for k, v in self.marbles_pos.items():
            if v in reset_list:
                self.marbles_pos[k] = reset_color
        if new_color: self.marbles_pos[target] = new_color

    def set_buffers(self, marble=None) -> None:
        """
        TODO
        """
        if marble:
            self.buffer_marble = marble
            self.buffer_color = self.marbles_pos[self.buffer_marble]
        self.buffer_marbles_pos = {k: v for k, v in self.marbles_pos.items()}
        self.buffer_marbles_rect = deepcopy(self.marbles_rect)

    def apply_buffers(self) -> None:
        """Apply the buffers to get back to the previous game's state."""

        if self.buffer_marbles_pos: 
            self.marbles_pos = {k: v for k, v in self.buffer_marbles_pos.items()}
        if self.buffer_marbles_rect:
            self.marbles_rect = deepcopy(self.buffer_marbles_rect)

    def clear_buffers(self) -> None:
        """
        TODO
        """
        self.buffer_marbles_pos.clear()
        self.buffer_marbles_rect.clear()

    def clear_ranges(self) -> None:
        """
        TODO
        """
        self.marbles_range.clear()
        self.new_marbles_range.clear()

    def check_range_type(self):
        """
        TODO
        """
        len_range = len(self.marbles_range)
        if len_range in (2, 3):
            min_x = min(self.marbles_range, key=lambda t: t[0])[0]
            max_x = max(self.marbles_range, key=lambda t: t[0])[0]
            if (len(set(elem[1] for elem in self.marbles_range))) == 1:
                valid_len_x = (2 * MARBLE_SIZE) * (len_range - 1)
                if max_x - min_x == valid_len_x:
                    return 1
            else:
                min_y = min(self.marbles_range, key=lambda t: t[1])[1]
                max_y = max(self.marbles_range, key=lambda t: t[1])[1]
                valid_len_x = MARBLE_SIZE * (len_range - 1)
                valid_len_y = (2 * MARBLE_SIZE) * (len_range - 1)
                current_x_len = max_x - min_x
                current_y_len = max_y - min_y
                if current_x_len == valid_len_x and current_y_len == valid_len_y:
                    return 2
            return False
        return True
    
    def compute_new_range(self, target) -> None:
        """
        TODO
        """
        x, y = target
        l_x, l_y = self.marbles_range[-1][0], self.marbles_range[-1][1]
        k, j = self.predict_direction(x, y, l_x, l_y)
        for marble in self.marbles_range:
            if y == l_y:
                new_x = marble[0] + k * 2 * MARBLE_SIZE
                new_y = marble[1]
            else:
                new_x = marble[0] + k * MARBLE_SIZE
                new_y = marble[1] + j * 2 * MARBLE_SIZE
            self.new_marbles_range[(new_x, new_y)] = self.current_color
        try:
            valid_range = all(
                self.marbles_pos[elem] in (MARBLE_FREE, MARBLE_GREEN)
                for elem in self.new_marbles_range.keys())
        except KeyError:
            print("You're trying to select a marble out of bounds!")
            return False
        else:
            return valid_range

    def mark_valid_neighboors(self, current):
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
                self.marbles_pos[n] 
            except KeyError:
                continue
            else:
                if self.marbles_pos[n] == MARBLE_FREE:
                    self.marbles_pos[n] = MARBLE_GREEN
                elif self.marbles_pos[n] == MARBLE_BLUE:
                    self.marbles_pos[n] = MARBLE_BROWN

    def predict_direction(self, x, y, l_x, l_y):
        """
        TODO
        """
        k = 1 if x > l_x else -1
        j = 1 if y > l_y else -1
        return k, j

    def push_marbles(self, target):
        end_move = False
        enemy = self.enemy(self.current_color)
        x, y = self.buffer_marble
        t_x, t_y = target
        while not end_move:
            sumito = enemy in self.marbles_range.values()
            too_much_marbles = (
                self.new_marbles_range.values.count(self.current_color) > 3
            )
            wrong_sumito = (
                self.new_marbles_range.count(enemy) 
                >= self.new_marbles_range.count(self.current_color)
            )
            if too_much_marbles or wrong_sumito:
                for marble in self.new_marbles_range.keys():
                    self.recolor_marbles(
                        marble, 
                        [MARBLE_BLUE, MARBLE_YELLOW], 
                        MARBLE_FREE, 
                        MARBLE_RED)

    def select_single_marble(self, mouse_pos, current_marble) -> None:
        """
        TODO
        """
        target = None
        init_marble = self.buffer_marble
        for t in self.marbles_rect:
            target = t.topleft
            if t.collidepoint(mouse_pos) and current_marble != t:
                self.apply_buffers()
                self.marbles_pos[init_marble] = MARBLE_FREE
                if init_marble != t.topleft:
                    self.clear_ranges()
                    if self.is_valid_neighboor(target, False):
                        if self.marbles_pos[target] == MARBLE_FREE:
                            self.marbles_pos[target] = MARBLE_GREEN
                            self.marbles_range.add(self.buffer_marble)
                            self.new_marbles_range[target] = self.current_color
                        else:
                            self.marbles_pos[target] = MARBLE_BROWN
                            # self.push_marbles(current_color)
                    else:
                        self.marbles_pos[target] = MARBLE_RED

    def select_marbles_range(self, mouse_pos):
        """
        TODO
        """
        for r in self.marbles_rect:
            if self.is_inside_marble(mouse_pos, r.center): 
                # first select a valid range of marbles (max 3)
                valid_range = self.check_range_type()
                if self.marbles_pos[r.topleft] in (self.current_color, MARBLE_PURPLE):
                    max_range = len(self.marbles_range) >= 3
                    if not max_range and valid_range:
                        self.marbles_range.add(r.topleft)
                        self.marbles_pos[r.topleft] = MARBLE_PURPLE

                # then color the new positions in green (if possible)
                elif (self.marbles_pos[r.topleft] == MARBLE_FREE
                      and len(self.marbles_range) > 1
                    ):
                    h_range = valid_range == "horizontal"
                    self.buffer_marble = self.marbles_range[-1]
                    valid_neighboor = self.is_valid_neighboor(
                        r.topleft, 
                        h_range)
                    valid_new_range = self.compute_new_range(r.topleft)
                    if valid_new_range and valid_neighboor:
                        for marble in self.new_marbles_range.keys():
                            self.recolor_marbles(
                                marble, 
                                [MARBLE_RED], 
                                MARBLE_FREE, 
                                MARBLE_GREEN)
                    else:
                        self.recolor_marbles(
                            r.topleft, 
                            [MARBLE_GREEN, MARBLE_RED], 
                            MARBLE_FREE, 
                            MARBLE_RED)
                        self.new_marbles_range.clear()

    def update_board(self):
        """
        TODO
        """
        if self.new_marbles_range:
            for old, new in zip(self.marbles_range, self.new_marbles_range.keys()):
                self.marbles_pos[old] = MARBLE_FREE
                self.marbles_pos[new] = self.current_color
            self.current_color = self.enemy(self.current_color)
        self.clear_ranges()

    def display_current_color(self, screen):
        font = pygame.font.SysFont("Sans", 35)
        if self.current_color == MARBLE_YELLOW:
            text = font.render("Yellow", True, YELLOW)
        else:
            text = font.render("Blue", True, BLUE)
        text_rect = text.get_rect(center=(SIZE_X /2, 20))
        screen.blit(text, text_rect)

    def reset_game(self) -> None:
        """
        TODO
        """
        self.build_marbles()
        self.clear_buffers()
        self.clear_ranges()

    @staticmethod
    def enemy(current_color):
        """Returns the enemy of the current color being played."""
        return MARBLE_BLUE if current_color == MARBLE_YELLOW else MARBLE_YELLOW

    @staticmethod
    def is_inside_marble(marble_center, mouse_pos) -> bool:
        x_mouse, y_mouse = mouse_pos
        x_marble, y_marble = marble_center
        d_mouse_center = (x_mouse - x_marble)**2 + (y_mouse - y_marble)**2
        d_mouse_center = math.sqrt(d_mouse_center)
        is_in_marble = d_mouse_center <= MARBLE_SIZE
        return is_in_marble

    @staticmethod
    def display_time_elasped(screen):
        """
        TODO
        """
        time_elasped = f"Time: {int(pygame.time.get_ticks() / 1e3)} s"
        screen.blit(FONT.render(time_elasped, True, WHITE), (10, 10))


# --------------------------------------------------------------

if __name__ == "__main__":
    pass
























