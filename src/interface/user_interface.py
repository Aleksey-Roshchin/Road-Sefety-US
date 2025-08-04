import os, time, shutil
from pathlib import Path
from src.constants import SRC_PATH, USER_INPUT_FORM, EXIT_COMMANDS
import src.analysis as analysis

# Consts
MENUS_PATH = SRC_PATH + r'/interface/menus'
PROGRAM_LOGO = MENUS_PATH + r"/program_logo.txt"
MAIN_MENU = MENUS_PATH + r'/main_menu.txt'
MAIN_MENU_LOGO = MAIN_MENU.rstrip('.txt') + '_logo.txt'
PRESET_REPORTS_MENU = MENUS_PATH + r'/preset_reports_menu.txt'
PRESET_REPORTS_LOGO = PRESET_REPORTS_MENU.rstrip('.txt') + '_logo.txt'

# Utils
def clear():
    os.system('clear')

def press_to_continue():
    input('\nPress Enter to continue')

def exit_program(user_input):
    if user_input.strip().lower() in EXIT_COMMANDS:
        print("\nExiting program...\n")
        time.sleep(1)
        exit()

def print_centered(text):
    width = shutil.get_terminal_size().columns
    padding = (width - len(text)) // 2
    print(" " * max(padding, 0) + text, end='')

def filepath_ckeck(filepath):
    try:
        with open(filepath) as f:
            return None
    except FileNotFoundError:
        print(f'File {filepath} not found.\nPlease check the file name.')
        exit()

def print_logo(filepath):
    filepath_ckeck(filepath)
    with open(filepath, 'r') as f:
        print(f.read())

def print_logo_centered(filepath):
    filepath_ckeck(filepath)
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


        


# Menus

def main_menu(df):
    print_menu(MAIN_MENU)
    user_input = input(f'\nChoose the available one:{USER_INPUT_FORM}')
    exit_program(user_input)
    match user_input:
        case "1":
            preset_reports_menu(df)
        case "2":
            pass
        case "3":
            pass
        case "4":
            pass
        case _:
            print('\nNot an option!')
            time.sleep(1)
            main_menu()
    

def preset_reports_menu(df):
    print_menu(PRESET_REPORTS_MENU)
    user_input = input(f'\nChoose the available one:{USER_INPUT_FORM}')
    exit_program(user_input)
    match user_input:
        case "1":
            print(analysis.cities_count(df))
            press_to_continue()
        case "2":
            pass
        case "3":
            pass
        case "4":
            pass
        case _:
            print('\nNot an option!')
            time.sleep(1)
            main_menu()


def custom_reports_menu():
    pass


def help():
    pass