import pygame
import math
import random

from pygame.locals import *
from constants import *
from ordered_set import OrderedSet
from copy import deepcopy
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" %(100, 100)
pygame.init()


class Abalone(pygame.sprite.Sprite):
    """
    A class used to represent a standard Abalone board.
    
    Attributes
    ----------
    configuration: string (optional, default="STANDARD")
        Board's initial configuration.
    marbles_rect: list
        Rectangles representing all marbles positions.
    marbles_pos: dict
        Marbles positions and its associated current value.
    buffer_marble: pygame.Surface
        Initial position of a marble being moved
    buffer_marbles_pos: dict
        Buffer of marbles_pos used to freeze the board's state
    marbles_2_change: dict
        Marbles to change when updating the board (if possible).
    buffer_line: string
        A visual green line used to emphazise push move
    current_color: pygame.Surface
        Current marble's color that is being played (MARBLE_BLUE or MARBLE_YELLOW)
    buffer_message: string
        Message used to inform the player of an incorrect move

    Methods
    -------
    build_marbles() -> None
        Place the marbles to their initial position.

    Static Methods
    --------------
    next_spot(r, c, orientation) -> tuple 
        Compute the next spot of a given one.
    
    """
    def __init__(self, configuration=STANDARD):
        """
        TODO
        """
        super().__init__()
        self.configuration = configuration
        self.marbles_rect = []  # Actually needed? (I think so)
        self.marbles_pos = dict()
        self.dead_zone = dict()
        self.marbles_2_change = dict()
        self.buffer_dead_zone = dict()
        self.buffer_line = None
        self.buffer_message = None
        self.buffer_marble = None
        self.buffer_color = None
        self.buffer_marbles_pos = dict()
        self.buffer_marbles_rect = []
        self.current_color = random.choice((MARBLE_BLUE, MARBLE_YELLOW))
        self.build_marbles()

    def build_marbles(self) -> None:
        """Place the marbles to their initial position."""
        
        y_init = 30
        gap_y = MARBLE_SIZE
        for row in self.configuration:
            x_init = SIZE_X - 400 - len(row) * MARBLE_SIZE
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

    def display_marbles(self, screen) -> None:
        """
        TODO
        """
        screen.fill(BACKGROUND)
        skull_rect = SKULL.get_rect()

        for m_pos, m_color in self.marbles_pos.items():
            if m_color in (MARBLE_BLUE_ALPHA, MARBLE_YELLOW_ALPHA):
                screen.blit(m_color, m_pos)
                skull_rect.center = (m_pos[0] + SHIFT_X, m_pos[1] + SHIFT_Y)
                screen.blit(SKULL, skull_rect)
            else:
                screen.blit(m_color, m_pos)
        for key, value in self.buffer_dead_zone.items():
            screen.blit(value, key)
            skull_rect.center = (key[0] + SHIFT_X, key[1] + SHIFT_Y)
            screen.blit(SKULL, skull_rect)

    def is_valid_neighbor(self, target_pos, h_range=False) -> bool:
        """
        TODO
        """
        x, y = self.buffer_marble
        neighbors = [
            (x - MARBLE_SIZE, y - 2 * MARBLE_SIZE),
            (x + MARBLE_SIZE, y - 2 * MARBLE_SIZE),
            (x - MARBLE_SIZE, y + 2 * MARBLE_SIZE),
            (x + MARBLE_SIZE, y + 2 * MARBLE_SIZE),
        ]
        if not h_range:
            neighbors.extend([(x - 2 * MARBLE_SIZE, y),
                              (x + 2 * MARBLE_SIZE, y)])
        return target_pos in neighbors

    def recolor_marbles(self, target, reset_list, 
                        reset_color, new_color=None) -> None:
        """
        TODO
        """
        for key, value in self.marbles_pos.items():
            if value in reset_list:
                self.marbles_pos[key] = reset_color
        if new_color: 
            self.marbles_pos[target] = new_color

    def set_buffers(self, marble=None) -> None:
        """
        TODO
        """
        if marble:
            self.buffer_marble = marble
            self.buffer_color = self.marbles_pos[self.buffer_marble]
        self.buffer_marbles_pos = {key: value for key, value 
                                   in self.marbles_pos.items()}
        self.buffer_marbles_rect = deepcopy(self.marbles_rect)

    def apply_buffers(self) -> None:
        """Apply the buffers to get back to the previous game's state."""

        if self.buffer_marbles_pos: 
            self.marbles_pos = {key: value for key, value 
                                in self.buffer_marbles_pos.items()}
        if self.buffer_marbles_rect:
            self.marbles_rect = deepcopy(self.buffer_marbles_rect)

    def update_dead_zone(self):
        """
        TODO
        """
        for key, value in self.buffer_dead_zone.items():
            if key not in self.dead_zone.keys():
                self.dead_zone[key] = value

    def clear_buffers(self) -> None:
        """
        TODO
        """
        self.buffer_marbles_pos.clear()
        self.buffer_marbles_rect.clear()
        self.buffer_dead_zone.clear()
        self.buffer_message = None
        self.buffer_line = None

    def clear_ranges(self) -> None:
        """
        TODO
        """
        self.marbles_2_change.clear()

    def check_range_type(self):
        """
        TODO
        """
        len_range = len(self.marbles_2_change)
        if len_range == 1:
            return True
        min_x = min(self.marbles_2_change.keys(), key=lambda t: t[0])[0]
        max_x = max(self.marbles_2_change.keys(), key=lambda t: t[0])[0]
        if (len(set(elem[1] for elem in self.marbles_2_change.keys()))) == 1:
            valid_len_x = (2 * MARBLE_SIZE) * (len_range - 1)
            if max_x - min_x == valid_len_x:
                return True
        else:
            min_y = min(self.marbles_2_change.keys(), key=lambda t: t[1])[1]
            max_y = max(self.marbles_2_change.keys(), key=lambda t: t[1])[1]
            valid_len_x = MARBLE_SIZE * (len_range - 1)
            valid_len_y = (2 * MARBLE_SIZE) * (len_range - 1)
            current_x_len = max_x - min_x
            current_y_len = max_y - min_y
            if current_x_len == valid_len_x and current_y_len == valid_len_y:
                return True
        return False

    def push_marbles(self, target):
        move_coefficients = self.predict_direction(self.buffer_marble, target)
        enemy = self.enemy(self.current_color)
        colors = [self.current_color]
        colors_debug = [MARBLE_DEBUG[self.current_color]]
        self.marbles_2_change[self.buffer_marble] = MARBLE_FREE
        x, y = target
        lateral_move = self.buffer_marble[1] == y

        end_move = False
        while not end_move:
            try:
                self.buffer_marbles_pos[(x, y)]
            except KeyError:
                if current_spot in (self.current_color, enemy):
                    if current_spot == MARBLE_BLUE:
                        dead_spot = MARBLE_BLUE_ALPHA
                    else:
                        dead_spot = MARBLE_YELLOW_ALPHA
                    self.buffer_dead_zone[(x, y)] = dead_spot
                break
            
            # the buffer is used instead of the actual marble_pos
            current_spot = self.buffer_marbles_pos[(x, y)]
            sumito = enemy in colors
            own_marble = current_spot == self.current_color
            other_marble = current_spot in (enemy, MARBLE_FREE)

            if current_spot in (enemy, self.current_color):
                colors.append(current_spot)
                colors_debug.append(MARBLE_DEBUG[current_spot])

            too_much_marbles = colors.count(self.current_color) > 3
            wrong_sumito = (colors.count(enemy) 
                            >= colors.count(self.current_color))
            # if the move is incorrect
            if too_much_marbles or wrong_sumito:
                self.buffer_message = "Invalid move!"
                self.marbles_pos[target] = MARBLE_RED
                self.clear_ranges()
                break
            # if we keep finding our own marbles
            if own_marble and (x, y) not in self.marbles_2_change.keys():
                self.marbles_2_change[(x, y)] = self.current_color
            # we either find an enemy or an empty spot
            elif other_marble:
                if sumito:
                    self.marbles_2_change[(x, y)] = enemy
                else:
                    self.marbles_2_change[(x, y)] = self.current_color
                # loop ends if its a free spot
                if current_spot == MARBLE_FREE:
                    end_move = True
            x, y = self.next_spot((x, y), move_coefficients, lateral_move)
            
        if self.marbles_2_change:
            self.buffer_message = None
            list_keys = list(self.marbles_2_change)
            x1, y1 = list_keys[0][0], list_keys[0][1]
            x2, y2 = list_keys[-1][0], list_keys[-1][1]
            self.buffer_line = (
                (x1 + SHIFT_X, y1 + SHIFT_Y), 
                (x2 + SHIFT_X, y2 + SHIFT_Y)
            )

    def select_single_marble(self, mouse_pos, current_marble) -> None:
        """
        TODO
        """
        target = None
        self.buffer_line = None
        init_marble = self.buffer_marble
        self.buffer_dead_zone.clear()

        for t in self.marbles_rect:
            target = t.topleft
            if t.collidepoint(mouse_pos) and current_marble != t:
                self.apply_buffers()
                self.marbles_pos[init_marble] = MARBLE_FREE
                if init_marble != t.topleft:
                    self.clear_ranges()
                    if self.is_valid_neighbor(target, False):
                        if self.marbles_pos[target] == MARBLE_FREE:
                            self.buffer_message = None
                            self.marbles_pos[target] = MARBLE_GREEN
                            self.marbles_2_change[self.buffer_marble] = MARBLE_FREE
                            self.marbles_2_change[target] = self.current_color
                        else:
                            self.push_marbles(target)
                    else:
                        self.marbles_pos[target] = MARBLE_RED
                        self.buffer_message = "Incorrect spot!"

    def select_marbles_range(self, r):
        """
        TODO
        """
        # first select a valid range of marbles (max 3)
        if (self.marbles_pos[r.topleft] in (self.current_color, MARBLE_PURPLE)
            and MARBLE_RED not in self.marbles_pos.values()
        ):
            max_range = len(self.marbles_2_change) >= 3
            if not max_range:
                self.marbles_2_change[r.topleft] = MARBLE_FREE
                if self.check_range_type():
                    self.marbles_pos[r.topleft] = MARBLE_PURPLE

    def compute_new_marbles_range(self, r):
        """
        TODO
        """
        # then color the new positions in green (if possible)
        if (self.marbles_pos[r.topleft] == MARBLE_FREE
            and len(self.marbles_2_change) > 1
            and self.current_color not in self.marbles_2_change.values()
        ):
            list_keys = list(self.marbles_2_change.keys())
            last_entry = list_keys[-1]
            lateral_move = last_entry[1] == r.topleft[1]
            move_coefficients = (
                self.predict_direction(last_entry, r.topleft)
            )
            # checking if the new range is free
            valid_new_range = True
            for marble in list_keys:
                next_spot = (
                    self.next_spot(marble, move_coefficients, lateral_move)
                )
                self.marbles_2_change[next_spot] = self.current_color
                try:
                    self.buffer_marbles_pos[next_spot] 
                except KeyError:
                    print("Out of bounds selection!")
                    valid_new_range = False
                    break
                else:
                    valid_new_range = (
                        self.buffer_marbles_pos[next_spot] 
                        in (MARBLE_FREE, MARBLE_GREEN)
                    )
                    if not valid_new_range:
                        break
            if valid_new_range:
                for m_pos, m_color in self.marbles_2_change.items():
                    if m_color == self.current_color:
                        self.recolor_marbles(
                            m_pos, 
                            [MARBLE_RED], 
                            MARBLE_FREE, 
                            MARBLE_GREEN)
            else:
                self.recolor_marbles(
                    r.topleft, 
                    [MARBLE_GREEN, MARBLE_RED],
                    MARBLE_FREE, 
                    MARBLE_RED)
                self.marbles_2_change.clear()

    def update_board(self):
        """
        TODO
        """
        if self.current_color in self.marbles_2_change.values():
            for m_pos, m_color in self.marbles_2_change.items():
                self.marbles_pos[m_pos] = m_color
            self.current_color = self.enemy(self.current_color)
        for key, value in self.buffer_dead_zone.items():
            if key not in self.marbles_pos.keys():
                self.marbles_pos[key] = value
        self.clear_ranges()

    def display_current_color(self, screen):
        if self.current_color == MARBLE_YELLOW:
            text = FONT.render("Yellow", True, YELLOW_MARBLE)
        else:
            text = FONT.render("Blue", True, BLUE_MARBLE)
        screen.blit(text, (10, 50))

    def display_error_message(self, screen):
        if self.buffer_message:
            text = FONT.render(self.buffer_message, True, RED)
            screen.blit(text, (10, 90))

    def draw_circled_line(self, screen, width):
        """
        TODO
        """
        if self.buffer_line:
            x1, y1 = self.buffer_line[0]
            x2, y2 = self.buffer_line[1]
            pygame.draw.line(screen, GREEN_2, (x1, y1), (x2, y2), width)
            pygame.draw.circle(screen, GREEN_2, (x1, y1), width*1.2)
            pygame.draw.circle(screen, GREEN_2, (x2, y2), width*1.2)

    def reset_game(self) -> None:
        """
        TODO
        """
        self.build_marbles()
        self.clear_buffers()
        self.clear_ranges()
        self.dead_zone.clear()

    # --------------------------------------------------------------
    @staticmethod
    def predict_direction(origin, target):
        """
        TODO
        """
        k = 1 if target[0] > origin[0] else -1
        j = 1 if target[1] > origin[1] else -1
        return k, j

    @staticmethod
    def next_spot(origin, move_coefficients, lateral_move):
        """
        TODO
        """
        k, j = move_coefficients
        if lateral_move:
            x = origin[0] + k * 2 * MARBLE_SIZE
            y = origin[1]
        else:
            x = origin[0] + k * MARBLE_SIZE
            y = origin[1] + j * 2 * MARBLE_SIZE
        return x, y

    @staticmethod
    def enemy(current_color):
        """Returns the enemy of the current color being played."""
        return MARBLE_BLUE if current_color == MARBLE_YELLOW else MARBLE_YELLOW

    @staticmethod
    def collision_marbles(current_marble, target_marble):
        c_x, c_y = current_marble
        t_x, t_y = target_marble
        d_marbles = (c_x - t_x)**2 + (c_y - t_y)**2
        collision = math.sqrt(d_marbles) <= 2 * MARBLE_SIZE
        return collision

    @staticmethod
    def is_inside_marble(marble_center, mouse_pos) -> bool:
        x_mouse, y_mouse = mouse_pos
        x_marble, y_marble = marble_center
        d_mouse_center = (x_mouse - x_marble)**2 + (y_mouse - y_marble)**2
        is_in_marble = math.sqrt(d_mouse_center) <= MARBLE_SIZE
        return is_in_marble

    @staticmethod
    def display_time_elapsed(screen):
        """
        TODO
        """
        time_elapsed = f"Time: {int(pygame.time.get_ticks() / 1e3)} s"
        screen.blit(FONT.render(time_elapsed, True, WHITE), (10, 10))


# --------------------------------------------------------------

if __name__ == "__main__":
    pass



