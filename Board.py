# -------------------- #
#    Abalone Board     #
# -------------------- #

import math
import re
import itertools
import random

from more_itertools import sliced
from termcolor import colored
from UserMessages import ask_messages, err_messages, info_messages


class Board():
    """
    A class used to represent a standard Abalone board.

    Static variables
    ----------
    dimension: int
        Number of rows, columns of the board
    mid_point: int
        Middle row
    char_2_num: dict
        Dictionnary with key:value pairs string:int 
        such as "A":1, "B:2", etc.
        Used to convert coordinates.
    disp: dict
        Dictionnary with key:values pairs string:lambda function
        The key represents an orientation (i.e. "E" for East) and
        its associated value is a lambda function using 2 parameters.
        The dictionnary is used to compute new coordinates of a 
        given sport of the board
    r, g, c, y, w: string
        Define the color red, green, cyan, yellow and white, respectively
    to_color: function
        Lambda function to turn a string into a colored one 
        (s: string, c: color)
    
    Attributes
    ----------
    marbles: dict
        Dictionnary with key:values pairs int:int.
        The key represents a marbles color (i.e. 2 for red marbles,
        3 for green ones) and the associated value is the number
        of such marble still on the board.
        Both players start with an equal amount of 14 marbles.
    board: list
        Nested list (2 dimensional).
        Used to represent the board's state
        The list is filled with integer values such as:
        0: dead zone (if a marbles goes into it, it dies)
        1: empty spot
        2: red marble
        3: green marble

    Methods
    -------
    ask_move(color) -> tuple
        Ask the current player his move
    update_board(user_data, orientation, color) -> bool
        Update the current board if the move is possible
    check_win() -> bool
        Count the number of marbles still alive
    push_move(friend, user_data, orientation) -> dict
        Compute the new positions of moving marbles by pushing
        Returns True if the move is valid
    free_move(friend, user_data, orientation) -> dict
        Move a group of marbles in empty spots
        Returns True if the move is valid
    valid_neighborhood(marble, friend, enemy) -> list
        Computes all valid neighboors where a given marble can move
    debug_board() -> list
        Return a representation of the attribute self.board as a list
    real_board() -> list
        Return the current Abalone board as a nested list
    __str__() -> string
        Return a full representation of the object as a string

    Static Methods
    --------------
    next_spot(r, c, orientation) -> tuple 
        Compute the next spot of a given one.
    to_2d_list(user_data) -> tuple
        Converts coordinates of a given marble from the board to the nested list
    enemy(color) -> int
        Compute the enemy of the current color
    is_diagonal(user_data) -> bool
        Check if a range of marbles is aligned along a diagonal
    is_horizontal(user_data) -> bool
        Check if a range of marbles is aligned along a horizontal axis.
    
    """
    dead, free = 0, 1
    dimension = 11
    mid_point = math.floor(dimension / 2)
    char_2_num = {chr(ord("A") + i): i + 1 for i in range(9)}
    disp = {
        "E" : lambda r, c: (r, c + 1),
        "W" : lambda r, c: (r, c - 1),
        "NE": lambda r, c: (r - 1, c),
        "SW": lambda r, c: (r + 1, c),
        "NW": lambda r, c: (r - 1, c - 1),
        "SE": lambda r, c: (r + 1, c + 1),
    }
    r, g, c, y, w = "red", "green", "cyan", "yellow", "white"
    to_color = lambda s, c: colored(s, c, attrs=["bold"])

    # 0: f = forbidden spot
    # 1: e = empty spot
    # 2: w = white marble
    # 3: b = black marble
    num_2_char = {
        "0": " ",
        "1": to_color("o", w),
        "2": to_color("#", r),
        "3": to_color("x", g) 
    }

    # constructor
    # ---------------------------------------------------------------------

    def __init__(self):
        """Constructor. Initializes the board and a marbles counter.

        We assume the standard abalone initial configuration commonly 
        used, so the marbles initial position are hard-coded.

        Parameters
        ----------
        None
        """
        self.marbles = {2: 14, 3: 14}

        # We assume the standard initial configuration commonly used
        # So its hard-coded
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
                      [0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0],
                      [0, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0],
                      [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                      [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                      [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                      [0, 0, 0, 1, 1, 3, 3, 3, 1, 1, 0],
                      [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0],
                      [0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # methods
    # ---------------------------------------------------------------------

    def ask_move(self, color) -> tuple:
        """Ask the current player his move.

        The player is asked until his input is valid.
        It first checks if the type of movement is correct (push or free).
        Then it checks if the positions entered can be updated.
        For instance, an empty or an enemy spot cannot be directly moved.
        Once the input is valid, the method update_board is called.

        Parameter
        ---------
        color: int (positional)
            Player's current color

        Return
        -------
        data_user: tuple 
            The marble(s) the player wants to move
        orientation: string
            The orientation where the marble(s) are being moved
        """
        color_word = "Red" if color == 2 else "Green"
        print(Board.to_color(f"{color_word}, it's your turn!",
                             f"{color_word.lower()}") + "\n" + "-" * 22)
        print(self)

        valid_move = False
        while not valid_move:
            expr = r"^([A-Z][1-9]\s?){1,3}$"
            move = input(ask_messages("ASK_MARBLES"))
            if re.match(expr, move, re.IGNORECASE) is None:
                err_messages("ERR_INPUTS")
                continue
            user_data = tuple(sliced(move, 2))

            # check if the selection of multiple marbles is correct
            diagonal = self.is_diagonal(user_data)
            horizontal = self.is_horizontal(user_data)
            if len(user_data) > 1:
                if not diagonal and not horizontal:
                    err_messages("ERR_RANGE")
                    continue

            # pairs construction in the 2d list frame
            data_2d_list = (self.to_2d_list(c) for c in user_data)
            data_2d_list = tuple(data_2d_list)
            
            # check if all the selected marbles have the same color
            values = tuple(self.board[r][c] for r, c in data_2d_list)
            if not all(e == color for e in values):
                err_messages("ERR_WRONG_MARBLES")
                continue
            valid_move = True

        # check if the orientation is correct
        ori = ["W", "E", "NW", "SE", "NE", "SW"]
        valid_orientation = False
        while not valid_orientation:
            sep = ", "
            orientation = input(ask_messages("ASK_ORIENTATION")).upper()
            if orientation.upper() not in ori:
                err_messages("ERR_ORIENTATION")
                continue
            valid_orientation = True

        return user_data, orientation

    def update_board(self, user_data, orientation, color) -> bool:
        """Update the board with new values.

        This method is called after submitting a correct move.
        It initializes an empty dict and passes it to methods which
        will fill it. The method call depends on the player's move.
        If the player gives more than one marble, then its a "free move".
        Otherwise, its a "push move", the marbles are being pushed.

        Parameters
        ----------
        user_data: tuple of strings (required)
            Inputs given by the user and describe its move
        color: int (required):
            Current player's color
        enemy: int (required)
            Current's player enemy

        Return
        -------
        new_data: dict
            Dict containing positions to be updated. However, it is
            possible that the player's move is incorrect. For instance, 
            a wrong sumito cannot be taken in consideration.
            If new_data has been filled, then the board gets an update.
            Otherwise inputs are being asked again to the player.
        """
        new_data = dict()
        if len(user_data) > 1:
            new_data = self.free_move(color,user_data, orientation)
        else:
            new_data = self.push_move(color, user_data, orientation)

        # Updating board if possible
        if new_data:
            for key, value in new_data.items():
                row, col = key
                self.board[row][col] = value

        print("new_data = ", new_data)    
        return new_data

    def check_win(self) -> bool:
        """Count the number of marbles still alive. 

        This method is used to check any (red or green) winning condition.
        Both players start with 14 marbles. One loses when 6 of his marbles
        are out.
        
        Parameter
        ---------
        None

        Return
        ------
        game_over: bool
            True if any color won the game, False otherwise
        """
        game_over = False
        red_wins = self.marbles[3] == 14 - 6
        green_wins = self.marbles[2] == 14 - 6
        if red_wins or green_wins:
            if red_wins:
                info_messages("INFO_RED_WINS")
            else:
                info_messages("INFO_GREEN_WNS")
            game_over = True
        
        return game_over
                
    def push_move(self, friend, user_data, orientation) -> dict:
        """Try to push marbles in a given direction.

        This method is used whenever the player wants to push multiple
        marbles. It also deals with sumito cases. If the move is incorrect,
        i.e. the player is try to push more than 3 of is own marbles, or if
        a sumito is invalid, it returns False. If the move is valid, it 
        returns True and fill a dictionnary (new_data) with the corresponding
        new positions.

        Parameters
        ----------
        friend: int
            Current player's color
        user_data: tuple
            The first marble on which the push is being performed
        orientation: string
            The orientation in which the push is being performed

        Return
        ------
        new_data: dict
            dict of key:value pairs tuple:int where the tuples
            represent the new positions or marbles and their new value
        """
        enemy = self.enemy(friend)
        r, c = self.to_2d_list(user_data[0])
        new_data = {(r, c): 1}  # the first marble becomes empty
        colors = [self.board[r][c]]

        while self.board[r][c] != Board.free:
            n_r, n_c = self.next_spot(r, c, orientation)
            current_spot = self.board[r][c]
            next_spot = self.board[n_r][n_c]
            colors.append(next_spot)

            sumito = enemy in colors
            too_much_marbles = colors.count(friend) > 3
            wrong_sumito = colors.count(enemy) >= colors.count(friend)

            # cannot push more than 3 marbles
            if too_much_marbles:
                err_messages("ERR_TOO_MUCH")
                new_data.clear()
                break
            # next spot is always friendly, except deadzone
            if current_spot == friend:
                if next_spot in (friend, enemy, Board.free):
                    new_data[(n_r, n_c)] = friend
                else:
                    # friend pushed to deadzone
                    info_messages("INFO_SUICIDE")
                    self.marbles[friend] -= 1
                    break
            # next spot depends on the sumito
            elif current_spot == enemy:
                if next_spot in (enemy, Board.free):
                    new_data[(n_r, n_c)] = enemy if sumito else enemy
                elif next_spot == friend:
                    wrong_sumito = True
                else:
                    # enemy pushed to deadzone
                    info_messages("INFO_KILL_ENEMY")
                    self.marbles[enemy] -= 1
                    break

            # performing a wrong sumito
            if wrong_sumito:
                err_messages("ERR_SUMITO")
                new_data.clear()
                break

            r, c = n_r, n_c

        return new_data

    def free_move(self, friend, user_data, orientation) -> bool:
        """Try to freely move marbles in a given direction.

        This method is used whenever the player wants to freely multiple
        marbles. It thus does not deal with sumito cases. If the move is incorrect,
        i.e. the player is try to move more than 3 of is own marbles, or if
        one of the next spot is invalid, it returns False. If the move is valid, it 
        returns True and fill a dictionnary (new_data) with the corresponding
        new positions.

        Parameters
        ----------
        friend: int
            Current player's color
        user_data: tuple
            The first marble on which the push is being performed
        orientation: string
            The orientation in which the push is being performed

        Return
        ------
        new_data: dict
            dict of key:value pairs tuple:int where the tuples
            represent the new positions or marbles and their new value
        """
        enemy = self.enemy(friend)
        new_data = dict()

        for element in user_data:
            valid_neighbors = self.valid_neighborhood(element, 
                                                      friend,
                                                      enemy)
            r, c = self.to_2d_list(element)
            n_r, n_c = self.next_spot(r, c, orientation)
            if (n_r, n_c) not in valid_neighbors:
                err_messages("ERR_EMPTY_SPOT")
                new_data.clear()
                break
            new_data[(r, c)] = 1
            if self.board[n_r][n_c] == 1:
                new_data[(n_r, n_c)] = friend
            else:
                info_messages("INFO_SUICIDE")
                self.marbles[friend] -= 1

        return new_data

    def valid_neighborhood(self, marble, friend, enemy) -> list:
        """Compute where a given marble can move.

        Method called whenever the player wants to freely move marbles.
        It thus is called only if move_marbles is called
        A given marble can be moved into an empty spot or the dead
        zone (which corresponds to killing a own marble).
            
        Parameter
        ---------
        marble: string (positional)
            The marble the player wants to move
        color: int (positional)
            Player's current move
        enemy: int (positional)
            Player's current enemy

        Return
        -------
        valid_neighborhood: list
            All the valid locations where the marble can be moved
        """
        valid_neighborhood = []
        r, c = self.to_2d_list(marble)
        for fun in Board.disp.values():
            n_r, n_c = fun(r, c)
            if self.board[n_r][n_c] not in (friend, enemy):
                valid_neighborhood.append((n_r, n_c))
                
        return valid_neighborhood

    def debug_board(self) -> list:
        """Return a representation of the attribute self.board as a list

        Parameters
        ----------
        None

        Return
        ------
        debug_board: list
            Representation of self.board
        """
        debug_board_list = []
        for i in range(1, Board.dimension - 1):
            num = colored(str(i), Board.c)
            debug_board_str = num
            debug_board_str += " ".join(list(Board.num_2_char[str(e)]
                                             for e in self.board[i]))
            debug_board_list.append(debug_board_str)

        nums = list(str(i) for i in range(1, Board.dimension - 1))
        nums = " ".join(nums)
        debug_board_list.append(f"   {colored(nums, Board.c)}  ")
        
        return debug_board_list
        
    def real_board(self) -> list:
        """Return the current Abalone board as a nested list.
        
        Parameters
        ----------
        None

        Return
        -------
        real_board_list: list
            Represents the actual hexagonal Abalone board 
        """
        real_board_list = []
        k = Board.dimension - 2
        for i in range(1, Board.dimension - 1):
            letter = colored(chr(ord("A") + i - 1), Board.c)
            real_board_str = f"{letter} "
            real_board_str += " ".join(list(Board.num_2_char[str(e)]
                                            for e in self.board[i]
                                            if e != 0))
            if i > math.floor(Board.dimension // 2):
                real_board_str += f" {colored(k, Board.y)}"
                k -= 1
            real_board_list.append(real_board_str)

        nums = list(str(i) for i in range(1, (Board.dimension // 2) + 1))
        nums = " ".join(nums)
        real_board_list.append(f"  {colored(nums, Board.y)}")

        return real_board_list

    def debug_str(self) -> str:
        """Returns a schematics representation of the 2d-list and the hexagonal board.

        This method is only used for debugging purposes.

        Parameters
        ----------
        None

        Return
        ------
        debug_str: string
            Represents the 2d-list and the actual hexagonal Abalone board.
        """
        dboard = self.debug_board()
        rboard = self.real_board()
        debug_str = "\n"
        j = 2
        k = 2 * j
        sep = " "

        for i, (row_dboard, row_rboard) in enumerate(zip(dboard, rboard)):
            if i < math.floor(Board.dimension // 2):
                full_row = f"{row_dboard} |  {k * sep}{row_rboard}\n"
                k -= 1
            elif i > math.floor(Board.dimension // 2):
                full_row = f"{row_dboard} |  {j * sep}{row_rboard}\n"
                j += 1
            else:
                full_row = f"{row_dboard} |   {row_rboard}\n"
            debug_str += full_row

        return debug_str

    def __str__(self) -> str:
        """Return a full representation of the object as a string.
        
        Parameter
        ---------
        None
        
        Return
        -------
        full_representation: string
            Orientations schematics and current board's state
        """
        orientations = Board.to_color("ORIENTATIONS", Board.w)
        board = Board.to_color("BOARD", Board.w)
        board_iter = iter(self.real_board())
        
        dead_zone = Board.to_color("DEAD-ZONE", Board.w)
        dead_red = f"Red: {14 - self.marbles[2]}"
        dead_red = Board.to_color(dead_red, Board.r)
        dead_green = f"Green: {14 - self.marbles[3]}"
        dead_green = Board.to_color(dead_green, Board.g)

        r_numbers = " ".join(list(colored(str(e), Board.y)
                                  for e in range(1, 6)))

        full_representation = (
            f"""
          {orientations}                      {board}        {dead_zone}
                                |        {next(board_iter)}     {dead_red}
            NW     NE           |       {next(board_iter)}    {dead_green}
              \   /             |      {next(board_iter)}
               \ /              |     {next(board_iter)}
        W ----- 0 ----- E       |    {next(board_iter)}
               / \              |     {next(board_iter)}
              /   \             |      {next(board_iter)}
            SW     SE           |       {next(board_iter)}
                                |        {next(board_iter)}
                                |         {next(board_iter)}
        """
        )
        return full_representation

    def set_test_board(self):
        """Set an experimental board used to perform tests.

        Paremeters
        ----------
        None

        Return
        ------
        self.board: list (nested)
            Attribute board
        """
        return self.board

    # static methods
    # ---------------------------------------------------------------------

    @staticmethod
    def next_spot(r, c, orientation) -> tuple:
        """Compute the next spot of a given one.

        Parameters
        ----------
        r: int (positional)
            Row number of the given spot in the 2d-list frame
        c: int (positional)
            Column number of the given spot in the 2d-list frame
        orientation: string (positional)
            Orientation in which the next's spot is being computed

        Return
        ------
        next spot: tuple of ints:
            new coordinates (row, col) in the 2d-list frame
        """
        next_spot = Board.disp[orientation.upper()](r, c)
        return next_spot

    @staticmethod
    def to_2d_list(user_data) -> tuple:
        """Converts coordinates of a given marble from the board to the nested list.

        Translates the coordinates of a given spot on the hexagonal
        board (i.e: "G3") into a valid row-column couple used by
        the 2d-list (self.board)

        Parameters
        ----------
        coords_hexa: string (positional)
            Coordinates of a given spot on the hexagonal board

        Return
        ------
        n_r, n_c: tuple (int)
            Coordinates of the given spot in the 2d-list (self.board)
        """
        r, c = user_data.upper()
        n_r = Board.char_2_num[r]
        n_c = int(c) + (ord(r) - ord("A")) - Board.mid_point + 1

        return n_r, n_c

    @staticmethod
    def enemy(color):
        """Compute the enemy of the current color.

        Parameter
        ---------
        color: int (positional)
            Current player's color

        Return
        ------
        enemy: int
            Current player's enemy

        """
        enemy: int = color + 1 if color == 2 else color - 1
        return enemy
            
    @staticmethod
    def is_diagonal(user_data) -> bool:
        """Check if a range of marbles is aligned along a diagonal.
            
        Parameters
        ----------
        user_data: tuple (positional)
            Range of marbles given by the user
            
        Return
        ------
        is_diagonal: bool
            True if the range is a diagonal, False otherwise
        """        
        min_r = min(user_data, key=lambda t: t[0])[0].upper()
        max_r = max(user_data, key=lambda t: t[0])[0].upper()
        is_diagonal: bool = (
            len(set(e[1] for e in user_data)) == 1
            and ord(max_r) - ord(min_r) < len(user_data)
        )
        return is_diagonal

    @staticmethod
    def is_horizontal(user_data) -> bool:
        """Check if a range of marbles is aligned along a horizontal axis.
            
        Parameters
        ----------
        user_data: tuple (positional)
            Range of marbles given by the user
            
        Return
        ------
        is_horizontal: bool
            True if the range is horizontal, False otherwise
        """
        min_c = min(user_data, key=lambda t: t[1])[1]
        max_c = max(user_data, key=lambda t: t[1])[1]
        is_horizontal: bool = (
            len(set(e[0] for e in user_data)) == 1
            and int(max_c) - int(min_c) < len(user_data)
        )
        return is_horizontal

def play_again() -> bool:
    """Ask the user if he wants to keep playing.

    Parameters
    ----------
    None

    Return
    ------
    True if the user wants to play again, False otherwise
    """
    while True:
        play_game = input('Play again (y/n)? : ')
        if re.search(r'^y|n{1}$', play_game, re.IGNORECASE) is None:
            print('Please enter \'y\', \'Y\', \'n\' or \'N\'')
            continue
        if re.search(r'^y{1}$', play_game, re.IGNORECASE):
            play_again = True
        elif re.search(r'^n{1}$', play_game, re.IGNORECASE):
            play_again = False
        break

def main() -> None:
    
    while True:
        B = Board()
        color = random.choice((2, 3))
        game_over = False
        while not game_over:
            user_data, orientation = B.ask_move(color)
            valid_move = B.update_board(user_data, orientation, color)
            game_over = B.check_win()
            if not valid_move:
                continue
            color = color
        if play_again():
            continue
        else:
            print("Bye...")
            break

if __name__ == "__main__":
    main()


