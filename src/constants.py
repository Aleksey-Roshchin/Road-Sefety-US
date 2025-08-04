import os
from pathlib import Path

# File paths
ROOT_PATH = str(Path(__file__).resolve().parent.parent)
SRC_PATH = str(Path(__file__).resolve().parent)
MENUS_PATH = SRC_PATH + r'/interface/menus'
PROGRAM_LOGO = MENUS_PATH + r"/program_logo.txt"
MAIN_MENU = MENUS_PATH + r'/main_menu.txt'
MAIN_MENU_LOGO = MAIN_MENU.rstrip('.txt') + '_logo.txt'
PRESET_REPORTS_MENU = MENUS_PATH + r'/preset_reports_menu.txt'
PRESET_REPORTS_LOGO = MENUS_PATH + r'/preset_reports_logo.txt'
CSV = ROOT_PATH + r'/data/raw/US_Accidents_March23.csv'

# Other consts
NUM_ROWS = 5    # Uses for display a certain quantity of rows
EXIT_COMMANDS = (
    "break",
    "bye",
    "close",
    "close app",
    "end",
    "end program",
    "exit",
    "exit program",
    "goodbye",
    "halt",
    "i want to quit",
    "i'm done",
    "kill",
    "kill program",
    "let me out",
    "quit",
    "quit program",
    "see you",
    "shut down",
    "stop",
    "stop program",
    "terminate",
    "terminate program",
    "that's it"
)

USER_INPUT_FORM = "\n\n>> "
