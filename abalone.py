from typing import Collection
import pygame
import os
import math

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
        self.new_marbles_range = set()
        self.buffer_marble = None
        self.buffer_color = None
        self.buffer_marbles_pos = dict()
        self.buffer_marbles_rect = []

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
                    return "horizontal"
            else:
                min_y = min(self.marbles_range, key=lambda t: t[1])[1]
                max_y = max(self.marbles_range, key=lambda t: t[1])[1]
                valid_len_x = MARBLE_SIZE * (len_range - 1)
                valid_len_y = (2 * MARBLE_SIZE) * (len_range - 1)
                current_x_len = max_x - min_x
                current_y_len = max_y - min_y
                if current_x_len == valid_len_x and current_y_len == valid_len_y:
                    return "diagonal"
            return False
        return True
    
    def compute_new_range(self, target, range_type) -> None:
        """
        TODO
        """
        last_marble = self.marbles_range[-1]
        first_marble = self.marbles_range[0]
        if range_type == "horizontal":
            r_x = last_marble[0]
            l_x = first_marble[0]
            k = 1 if l_x > r_x else -1
            for i in range(len(self.marbles_range)):
                new_x = target[0] + k * 2 * i * MARBLE_SIZE, 
                new_y = target[1]
                self.new_marbles_range.add((new_x, new_y))
        else:
            x, y = target
            if y == last_marble[1]:
                k = 1 if x > last_marble[0] else - 1
                for elem in self.marbles_range:
                    new_x = elem[0] + k * MARBLE_SIZE
                    new_y = elem[1] 
                    self.new_marbles_range.add((new_x, new_y))
        print(self.marbles_range)
        print(self.new_marbles_range)

    def select_single_marble(self, mouse_pos, current) -> None:
        """
        TODO
        """
        target = None
        for t in self.marbles_rect:
            target = t.topleft
            if t.collidepoint(mouse_pos) and current != t:
                if (self.marbles_pos[target] == MARBLE_FREE):
                    valid_neighboor = self.is_valid_neighboor(t.topleft, False)
                    highlight = MARBLE_GREEN if valid_neighboor else MARBLE_RED
                    # The initial position isnt taken into consideration
                    if t.topleft != self.buffer_marble:
                        self.recolor_marbles(
                            target, 
                            [MARBLE_GREEN, MARBLE_RED], 
                            MARBLE_FREE, 
                            highlight)
                        self.clear_ranges()
                        if valid_neighboor:
                            self.marbles_range.add(self.buffer_marble)
                            self.new_marbles_range.add(target)

    def select_marbles_range(self, mouse_pos, current_color):
        """
        TODO
        """
        for r in self.marbles_rect:
            if self.is_inside_marble(mouse_pos, r.center): 
                # first select a valid range of marbles
                valid_range = self.check_range_type()
                if self.marbles_pos[r.topleft] in (current_color, MARBLE_PURPLE):
                    self.marbles_range.add(r.topleft)
                    max_range = len(self.marbles_range) <= 3
                    if max_range and valid_range:
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
                    self.compute_new_range(r.topleft, valid_range)
                    valid_new_range = all(
                        self.marbles_pos[elem] == MARBLE_FREE
                        for elem in self.new_marbles_range
                    )
                    if valid_new_range and valid_neighboor:
                        for marble in self.new_marbles_range:
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
                        self.clear_ranges()

    def update_board(self, current_color):
        """
        TODO
        """
        # print("old:", self.marbles_range, "\n", "new:", self.new_marbles_range)
        if self.new_marbles_range:
            for old_pos, new_pos in zip(self.marbles_range, self.new_marbles_range):
                self.marbles_pos[old_pos] = MARBLE_FREE
                self.marbles_pos[new_pos] = current_color
        self.clear_ranges()

    def reset_game(self) -> None:
        """
        TODO
        """
        self.build_marbles()
        self.clear_buffers()
        self.clear_ranges()

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
        screen.blit(FONT.render(time_elasped, True, TXT_COLOR), (10, 10))


# --------------------------------------------------------------

if __name__ == "__main__":
    pass
























