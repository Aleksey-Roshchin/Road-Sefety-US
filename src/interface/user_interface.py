import os, time, shutil
from pathlib import Path
from src.constants import MENUS_PATH, USER_INPUT_FORM

# Consts


# Utils
def clear():
    os.system('clear')

def print_centered(text):
    width = shutil.get_terminal_size().columns
    padding = (width - len(text)) // 2
    print(" " * max(padding, 0) + text, end='')

def filepath_ckeck(filepath):
    try:
        with open(filepath) as f:
            return None
    except FileNotFoundError:
        print(f'File {filepath} not found')
        exit()

def print_logo(filepath):
    with open(filepath, 'r') as f:
        print(f.read())

def print_logo_centered(filepath):
    with open(filepath, 'r') as f:
        for row in f.read().splitlines():
            print_centered(row)
            time.sleep(0.1)
            print()
        time.sleep(1)

def print_menu(filepath):
    filepath_ckeck(filepath)
    clear()
    print_logo(filepath.rstrip('.txt') + '_logo.txt')
    with open(filepath, 'r') as f:
        print(f.read())
    choice = input(f'\nChoose the available one:{USER_INPUT_FORM}')



# Menus

def main_menu():
    # clear()
    print_menu(MENUS_PATH + '/main.txt')
