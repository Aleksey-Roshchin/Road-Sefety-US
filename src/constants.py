import os
from pathlib import Path

# File paths
ROOT_PATH = str(Path(__file__).resolve().parent.parent)
SRC_PATH = str(Path(__file__).resolve().parent)
MENUS_PATH = SRC_PATH + r'/interface/menus'
PROGRAM_LOGO = MENUS_PATH + r"/program_logo.txt"
MAIN_MENU = MENUS_PATH + r'/main_menu.txt'
MAIN_MENU_LOGO = MAIN_MENU.rstrip('.txt') + '_logo.txt'



USER_INPUT_FORM = "\n\n>>> "
