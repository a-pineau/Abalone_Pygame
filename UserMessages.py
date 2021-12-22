# ---------------------- #
#      User Messages     #
# ---------------------- #
from termcolor import colored

def ask_messages(msg):
    """
    TODO
    """
    msg_color = "white"
    ask_msgs = {
        "ASK_MARBLES": colored(
            "Pick your marble(s) (A-I, 0-8): ",
            msg_color,
            attrs=["bold"]
        ),
        "ASK_ORIENTATION": colored(
            "Orientation (W, E, NW, SE, NE, SW)? ",
            msg_color,
            attrs=["bold"]
        ),
        "ASK_MOVEMENT": colored(
            "Do you want to push marbles or perform a free move?\n"
            + "P: push, F: free: ",
            msg_color,
            attrs=["bold"]
        ),
        "ASK_P_MARBLES": colored(
            "Select a marble and its next position: ",
            msg_color,
            attrs=["bold"]
        ),
        "ASK_F_MARBLES": colored(
            "Select a single marble or a range of marble. \n" +
            "In the case of a range, select the first and last marble.\n"
            "Also pick the next position of the first selected marble: ",
            msg_color,
            attrs=["bold"]
        )
    }
    return ask_msgs[msg]

def err_messages(msg):
    """
    TODO
    """
    msg_color = "red"
    err_msgs = {
        "ERR_MOVEMENT": colored(
            "Invalid movement!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_INPUTS": colored(
            "Invalid inputs!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_ORIENTATION": colored(
            "Invalid orientation!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_RANGE": colored(
            "The selected range is not valid!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_NON_FRIENDLY_RANGE": colored(
            "The selected range should contain only friendly marbles!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_WRONG_MARBLES": colored(
            "You have to select your own marble(s)!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_EMPTY_SPOT": colored(
            "You gotta select an empty spot!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_MOVE_RANGE": colored(
            "You cannot move your multiple marbles like this!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_TOO_MUCH": colored(
            "You cannot move more than 3 marbles!",
            msg_color,
            attrs=["bold"]
        ),
        "ERR_SUMITO": colored(
            "/!\ Wrong sumito! /!\\",
            msg_color,
            attrs=["bold"]
        )
    }
    print(err_msgs[msg])

def info_messages(msg):
    """
    TODO
    """
    msg_color = "yellow"
    info_msgs = {
        "INFO_SUICIDE": colored(
            "You\'ve killed your own marble(s). Nice.",
            msg_color,
            attrs=["bold"]
        ),
        "INFO_KILL_ENEMY": colored(
            "You've killed an enemy marble!",
            msg_color,
            attrs=["bold"]
        ),
        "INFO_RED_WINS": colored(
            "Red marbles win the game!",
            msg_color,
            attrs=["bold"]
        ),
        "INFO_GREEN_WINS": colored(
            "Green marbles win the game!",
            msg_color,
            attrs=["bold"]
        )
    }
    print(info_msgs[msg])



if __name__ == "__main__":
    pass # test

