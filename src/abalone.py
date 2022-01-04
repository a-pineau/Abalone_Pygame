import pygame
import math
import random

from pygame import gfxdraw
from pygame.locals import *
from constants import *
from ordered_set import OrderedSet
from copy import deepcopy
pygame.init()


class Abalone(pygame.sprite.Sprite):
    """
    A class used to represent a standard Abalone board.
    Both players have 14 marbles.
    A player loses whenever 6 of his marbles are out.
    
    Attributes
    ----------
    configuration: string (optional, default="STANDARD")
        Initial board configuration.
    marbles_rect: list
        Rectangles representing all marbles positions.
    marbles_pos: dict
        Marbles positions and its associated current value.
    buffer_marble: pygame.Surface
        Initial position of a marble being moved.
    buffer_marbles_pos: dict
        Buffer of marbles_pos used to freeze the board's state.
    marbles_2_change: dict
        Marbles to change when updating the board (if possible).
    buffer_line: string
        A visual green line used to emphazise push move.
    current_color: pygame.Surface
        Current marble's color that is being played (MARBLE_BLUE or MARBLE_YELLOW).
    buffer_message: string
        Message used to inform the player of an incorrect move.

    Methods
    -------
    build_marbles(self) -> None
        Place the marbles to their initial position.
    display_marbles(self, screen) -> None:
        Display the marbles, i.e. the board and both (blue and yellow) dead-zones.
    is_valid_neighbor(self, target_pos, h_range=False) -> bool:
        Check if a given marble is a valid neighbor.
    recolor_marbles(self, target, reset_list, reset_color, new_color=None) -> None:
        Recolor multiples marbles to have one colored marble (green or red)
    set_buffers(self, marble=None) -> None:
        Set buffers to keep track of the board's state at a given time.
    apply_buffers(self) -> None:
        Apply the buffers to get back to the previous game's state.
    clear_buffers(self) -> None:
        Clear the all the buffers at once.
    push_marbles(self, target) -> None:
        Performs a push move.
    select_single_marble(self, mouse_pos, current_marble) -> None:
        Select a single marble to be moved towards a valid spot.
    check_range_type(self) -> bool:
        Check if a range selection is valid.
    select_marbles_range(self, target) -> None:
        Select a range of connected marbles along a common axis.
    compute_new_marbles_range(self, target) -> None:
        Computes the new positions of a range of connected marbles.
    update_board(self) -> None:
        Update the state of the game.
    display_current_color(self, screen) -> None:
        Display the current color being played.
    display_error_message(self, screen) -> None:
        Display a red message whenever an invalid move is being played.
    draw_circled_line(self, screen, colour, width) -> None:
        Draw a line with two circles to enhance the visual effect.
    reset_game(self) -> None:
        Reset the game by pressing p (pygame constant K_p).

    Static Methods
    --------------
    predict_direction(origin, target) -> tuple:
        Predict the direction when computing new spot coordinates.
    compute_next_spot(origin, move_coefficients, lateral_move) -> tuple:
        Compute the next spot of given marble coordinates.
    enemy(current_color) -> pygame.Surface:
        Returns the enemy of the current color being played.
    is_inside_marble(marble_center, mouse_pos) -> bool:
        Check if the mouse cursor position is inside a marble.
    display_time_elapsed(screen) -> None:
        Display the time elapsed since the game was launched.

    """
    def __init__(self, configuration=STANDARD):
        """
        TODO
        """
        super().__init__()
        self.configuration = configuration
        self.marbles_rect = [] 
        self.marbles_pos = dict()
        self.dead_zone_blue = dict()
        self.dead_zone_yellow = dict()
        self.dead_marbles = {DEAD_BLUE: 0, DEAD_YELLOW: 0}
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

        self.dead_zone_blue = {
            (30, 120): MARBLE_FREE,
            (90, 120): MARBLE_FREE,
            (150, 120): MARBLE_FREE,
            (60, 180): MARBLE_FREE,
            (120, 180): MARBLE_FREE,
            (90, 240): MARBLE_FREE,
        }
        self.dead_zone_yellow = {
            (90, 360): MARBLE_FREE,
            (60, 420): MARBLE_FREE,
            (120, 420): MARBLE_FREE,
            (30, 480): MARBLE_FREE,
            (90, 480): MARBLE_FREE,
            (150, 480): MARBLE_FREE,
        }

    def display_marbles(self, screen) -> None:
        """Display the marbles, i.e. the board and both (blue and yellow) dead-zones.

        Parameter
        ---------
        screen: pygame.Surface (required)

        Return
        ------
        None
        """
        screen.fill(BACKGROUND)
        skull_rect = SKULL.get_rect()

        for m_pos, m_color in self.marbles_pos.items():
            screen.blit(m_color, m_pos)
        for k_dz, v_dz in self.buffer_dead_zone.items():
            screen.blit(v_dz, k_dz)
            skull_rect.center = (k_dz[0] + SHIFT_X, k_dz[1] + SHIFT_Y)
            screen.blit(SKULL, skull_rect)
        for k_blue, v_blue in self.dead_zone_blue.items():
            screen.blit(v_blue, k_blue)
            if v_blue != MARBLE_FREE:
                skull_rect.center = (k_blue[0] + SHIFT_X, k_blue[1] + SHIFT_Y)
                screen.blit(SKULL, skull_rect)
        for k_yellow, v_yellow in self.dead_zone_yellow.items():
            screen.blit(v_yellow, k_yellow)
            if v_yellow != MARBLE_FREE:
                skull_rect.center = (k_yellow[0] + SHIFT_X, k_yellow[1] + SHIFT_Y)
                screen.blit(SKULL, skull_rect)

    def is_valid_neighbor(self, target_pos, h_range=False) -> bool:
        """Check if a given marble is a valid neighbor.

        Parameters
        ----------
        target_pos: tuple of ints (required)
            Coordinates (x, y) of the target
        h_range: bool (optional, default=False)
            Used whenever a range is being moved laterally.
            In this case, the neighborhood is restricted to 4 neighbors
            instead of 6.

        Returns
        -------
        bool
            True if the target is a valid neighbor.
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

    def recolor_marbles(self, target, reset_list, reset_color, new_color=None) -> None:
        """Recolor multiples marbles to have one colored marble (green or red)

        This method is used when a marble becomes a valid neighbor (green) or not (red).
        If a previous marble's color was changed, it changes it to its previous value (free or solid)

        Parameters
        ----------
        target: pygame.Surface
            The current target (i.e. the marble being mouseover'd at)
        reset_list: list of pygame.Surface (required)
            A list of pygame.Surface we want to recolor
        reset_color: pygame.Surface (required)
            The previous color (free or solid)
        new_color: pygame.Surface (optional, default=None)
            The new color of the current target

        Returns
        -------
        None
        """
        for key, value in self.marbles_pos.items():
            if value in reset_list:
                self.marbles_pos[key] = reset_color
        if new_color:
            self.marbles_pos[target] = new_color

    def set_buffers(self, marble=None) -> None:
        """Set buffers to keep track of the board's state at a given time.

        Parameters
        ----------
        marble: pygame.Surface (optional, default=None)
            Used when moving freely a single marble.
            We want to keep track of its initial location

        Returns
        -------
        None
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

    def clear_buffers(self) -> None:
        """Clear the all the buffers at once.

        Method used when updating the board.
        """

        self.buffer_marbles_pos.clear()
        self.buffer_marbles_rect.clear()
        self.buffer_dead_zone.clear()
        self.buffer_message = None
        self.buffer_line = None

    def push_marbles(self, target) -> None:
        """Performs a push move.

        It includes pushing friendly marbles both with no sumito and sumito.
        It also checks if the move is possible. More than 3 friendly marbles cannot
        be moved at the same time. Also, a sumito can be invalid:
        If the number of enemy marbles is higher or equal to the number of
        friendly marbles. Or if an enemy marble is followed by a friendly marble.

        Parameters
        ----------
        target: pygame.Surface (required)

        Returns
        -------
        None
        """
        move_coefficients = self.predict_direction(self.buffer_marble, target)
        enemy = self.enemy(self.current_color)
        colors = [self.current_color]
        self.marbles_2_change[self.buffer_marble] = MARBLE_FREE
        x, y = target
        lateral_move = self.buffer_marble[1] == y

        end_move = False
        self.buffer_dead_zone.clear()
        while not end_move:
            try:
                self.buffer_marbles_pos[(x, y)]
            except KeyError:
                if current_spot in (self.current_color, enemy):
                    if current_spot == MARBLE_BLUE:
                        dead_spot = DEAD_BLUE
                    else:
                        dead_spot = DEAD_YELLOW
                    self.buffer_dead_zone[(x, y)] = dead_spot
                break

            # the buffer is used instead of the actual marble_pos
            current_spot = self.buffer_marbles_pos[(x, y)]
            sumito = enemy in colors
            own_marble = current_spot == self.current_color
            other_marble = current_spot in (enemy, MARBLE_FREE)

            if current_spot in (enemy, self.current_color):
                colors.append(current_spot)

            too_much_marbles = colors.count(self.current_color) > 3
            wrong_sumito = (colors.count(enemy) >= colors.count(self.current_color)
                            or enemy in colors and current_spot == self.current_color)
            # if the move is incorrect
            if too_much_marbles or wrong_sumito:
                self.buffer_message = "Invalid move!"
                self.marbles_pos[target] = MARBLE_RED
                self.marbles_2_change.clear()
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
            # getting the next spot
            x, y = self.compute_next_spot((x, y), move_coefficients, lateral_move)

        if self.marbles_2_change:
            self.buffer_message = None
            list_keys = list(self.marbles_2_change)
            x1, y1 = list_keys[0][0], list_keys[0][1]
            x2, y2 = list_keys[-1][0], list_keys[-1][1]
            self.buffer_line = (
                (x1 + SHIFT_X, y1 + SHIFT_Y),
                (x2 + SHIFT_X, y2 + SHIFT_Y))

    def select_single_marble(self, mouse_pos, current_marble) -> None:
        """Select a single marble to be moved towards a valid spot.

        A valid spot is a free/friendly spot in the current_marble neighborhood.
        If the spot is actually valid, its color changes from free to green (not permanent).
        Otherwise, it changes from free to red (not permanent).

        Parameters
        ----------
        mouse_pos: tuple of integers (required)
            The current mouse location.
        current_marble: pygame.Surface (required)
            The current marble being selected.

        Returns
        -------
        None
        """
        target = None
        self.buffer_line = None
        self.buffer_dead_zone.clear()
        init_marble = self.buffer_marble

        for t in self.marbles_rect:
            target = t.topleft
            if t.collidepoint(mouse_pos) and current_marble != t:
                self.apply_buffers()
                self.marbles_pos[init_marble] = MARBLE_FREE
                if init_marble != t.topleft:
                    self.marbles_2_change.clear()
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
                        self.buffer_message = "Invalid move!"

    def check_range_type(self) -> bool:
        """Check if a range selection is valid.
        
        Method used when moving connected marbles along a common axis.

        Returns
        -------
        bool
            True if the selected range is valid, False otherwise.
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

    def select_marbles_range(self, target) -> None:
        """Select a range of connected marbles along a common axis.

        As long as the range is valid, the marbles turn purple

        Parameter
        ---------
        target: pygame.Surface (required)
            Current target, i.e. the marble being mouseover'd at
        """
        if (self.marbles_pos[target.topleft] in (self.current_color, MARBLE_PURPLE)
            and MARBLE_RED not in self.marbles_pos.values()):
            max_range = len(self.marbles_2_change) >= 3
            if not max_range:
                self.marbles_2_change[target.topleft] = MARBLE_FREE
                if self.check_range_type():
                    self.marbles_pos[target.topleft] = MARBLE_PURPLE

    def compute_new_marbles_range(self, target) -> None:
        """Computes the new positions of a range of connected marbles.

        If all the marble can be moved into the new range, those spots
        become green. Otherwise, the targetted spot becomes red.

        Parameter
        ---------
        target: pygame.Surface (required)
            Current marble being mouseover'd at
        """
        
        if (self.marbles_pos[target.topleft] == MARBLE_FREE
            and len(self.marbles_2_change) > 1
            and self.current_color not in self.marbles_2_change.values()
        ):
            list_keys = list(self.marbles_2_change.keys())
            last_entry = list_keys[-1]
            lateral_move = last_entry[1] == target.topleft[1]
            move_coefficients = (
                self.predict_direction(last_entry, target.topleft))
            valid_new_range = True
            for marble in list_keys:
                next_spot = (
                    self.compute_next_spot(marble, move_coefficients, lateral_move))
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
                        in (MARBLE_FREE, MARBLE_GREEN))
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
                    target.topleft,
                    [MARBLE_GREEN, MARBLE_RED],
                    MARBLE_FREE,
                    MARBLE_RED)
                self.marbles_2_change.clear()

    def update_board(self) -> None:
        """Update the state of the game."""

        if self.current_color in self.marbles_2_change.values():
            for m_pos, m_color in self.marbles_2_change.items():
                self.marbles_pos[m_pos] = m_color
            self.current_color = self.enemy(self.current_color)
        for dz_value in self.buffer_dead_zone.values():
            if dz_value == DEAD_BLUE:
                for key, value in self.dead_zone_blue.items():
                    if value == MARBLE_FREE:
                        self.dead_zone_blue[key] = dz_value
                        break
            else:
                for key, value in self.dead_zone_yellow.items():
                    if value == MARBLE_FREE:
                        self.dead_zone_yellow[key] = dz_value
                        break
            self.dead_marbles[dz_value] += 1
        self.marbles_2_change.clear()

    def display_current_color(self, screen) -> None:
        """Display the current color being played.

        Parameter
        ---------
        screen: pygame.display (required)
            Game's window
        """

        if self.current_color == MARBLE_YELLOW:
            text = FONT.render("Yellow", True, YELLOW_MARBLE)
        else:
            text = FONT.render("Blue", True, BLUE_MARBLE)
        screen.blit(text, (5, 45))

    def display_error_message(self, screen) -> None:
        """Display a red message whenever an invalid move is being played."""

        if self.buffer_message:
            text = FONT.render(self.buffer_message, True, RED_2)
            screen.blit(text, (5, 85))

    def draw_circled_line(self, screen, colour, width) -> None:
        """Draw a line with two circles to enhance the visual effect.

        Parameters
        ----------
        screen: pygame.display (required)
            Game's window
        colour: tuple of integers (required)
            Colour's RGB code
        width: float (required)
            Line's width
        """

        if self.buffer_line:
            x1, y1 = self.buffer_line[0]
            x2, y2 = self.buffer_line[1]
            pygame.draw.line(screen, colour, (x1, y1), (x2, y2), width)
            gfxdraw.aacircle(screen, x1, y1, width + 1, colour)
            gfxdraw.filled_circle(screen, x1, y1, width + 1, colour)
            gfxdraw.aacircle(screen, x2, y2, width + 1, colour)
            gfxdraw.filled_circle(screen, x2, y2, width + 1, colour)

    def reset_game(self) -> None:
        """Reset the game by pressing p (pygame constant K_p)."""

        self.build_marbles()
        self.clear_buffers()
        self.marbles_2_change.clear()
        for key in self.dead_marbles.keys():
            self.dead_marbles[key] = 0
        for key in self.dead_zone_blue.keys():
            self.dead_zone_blue[key] = MARBLE_FREE
        for key in self.dead_zone_yellow.keys():
            self.dead_zone_yellow[key] = MARBLE_FREE

    # --------------------------------------------------------------

    @staticmethod
    def predict_direction(origin, target) -> tuple:
        """Predict the direction when computing new spot coordinates.

        Parameters
        --------- 
        origin: tuple of integers (required)
            First marble's coordinates
        target: tuple of integers (required)
            Second marble's coordinates

        Returns
        -------
        k, j: tuple of integers
            k: lateral coefficient
            j: vertical coefficient
        """

        k = 1 if target[0] > origin[0] else -1
        j = 1 if target[1] > origin[1] else -1
        return k, j

    @staticmethod
    def compute_next_spot(origin, move_coefficients, lateral_move) -> tuple:
        """Compute the next spot of given marble coordinates.

        Parameters
        ----------
        origin: tuple of integers (required)
            Initial marble.
        move_coefficients: tuple of integers (required)
            Lateral (k) and vertical (j) coefficients used to
            compute the next spot's direction.
        lateral_move: bool (required) 
            True if a lateral move (horizontal axis) is being performed.

        Returns
        -------
        x, y: tuple of integers
            Coordinates of the next spot.

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
    def enemy(current_color) -> pygame.Surface:
        """Returns the enemy of the current color being played."""

        return MARBLE_BLUE if current_color == MARBLE_YELLOW else MARBLE_YELLOW

    @staticmethod
    def is_inside_marble(marble_center, mouse_pos) -> bool:
        """Check if the mouse cursor position is inside a marble.

        Parameters
        ----------
        marble_center: tuple of integers (required)
            Marble's coordinates
        mouse_pos: tuple of integers (required)
            Cursor's coordinates

        Returns
        -------
        bool
            True if the mouse cursor is inside the marble,
            False otherwise.
        """

        x_mouse, y_mouse = mouse_pos
        x_marble, y_marble = marble_center
        d_mouse_center = (x_mouse - x_marble)**2 + (y_mouse - y_marble)**2
        return math.sqrt(d_mouse_center) <= MARBLE_SIZE

    @staticmethod
    def display_time_elapsed(screen) -> None:
        """Display the time elapsed since the game was launched.

        Parameter
        ---------
        screen: pygame.display
            Game's window
        """

        time_elapsed = f"Time: {int(pygame.time.get_ticks() / 1e3)}s"
        screen.blit(FONT.render(time_elapsed, True, WHITE), (5, 5))

# --------------------------------------------------------------

if __name__ == "__main__":
    pass



