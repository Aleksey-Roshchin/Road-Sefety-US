import pandas as pd
import os, time, shutil
from pathlib import Path
from src.constants import SRC_PATH, USER_INPUT_FORM, EXIT_COMMANDS
import src.visualization as visualization
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

def exit_program(user_input: str) -> None:
    if user_input.strip().lower() in EXIT_COMMANDS:
        print("\nExiting program...\n")
        time.sleep(1)
        exit()

def checked_input(message='') -> str:
    if message:
        print(message)
    user_input = input(USER_INPUT_FORM).lower().strip()
    exit_program(user_input)
    return user_input


def print_centered(text: str) -> None:
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
        time.sleep(0.2)

def print_menu(filepath):
    filepath_ckeck(filepath)
    clear()
    print_logo(filepath.rstrip('.txt') + '_logo.txt')
    with open(filepath, 'r') as f:
        print(f.read())

def ask_for_visualize(df, plot_title=None, chart_type='bar') -> None:
    user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\n2. No').lower()
    while user_input not in ("1", "y", "yes", '2', 'no', 'n'):
        print(f'\nYou entered {user_input} which is not an option! Please re-enter')
        time.sleep(1)
        user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\n2. No').lower()
    match user_input:
        case "1" | "y" | "yes":
            x_col, y_col = df.columns
            match chart_type:
                case 'bar':
                    visualization.bar_plot(df, x_col, y_col, plot_title=plot_title)
                case 'line':
                    visualization.line_plot(df, x_col, y_col, plot_title=plot_title)
        case '2' | 'no' | 'n':
            pass


def check_year(year: str) -> pd.Timestamp:
    valid_years = [str(y) for y in range(2016, 2024)]
    min_year = min(valid_years)
    max_year = max(valid_years)
    while year not in valid_years:
        year = checked_input(f'Not an option! Please, choose the year from {min_year} to {max_year}')
    return pd.to_datetime(year).year


def check_city(df: pd.DataFrame, city: str) -> str:
    valid_cities = df['City'].str.lower().unique()
    city = city.lower()
    while city not in valid_cities:
        city = checked_input(f'The data base has no this city. Please, check the city name.')
    return city

# Menus

def main_menu(df):
    print_menu(MAIN_MENU)
    user_input = checked_input('\nChoose the available one:')
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
    

def preset_reports_menu(df: pd.DataFrame):
    print_menu(PRESET_REPORTS_MENU)
    user_input = checked_input('\nChoose the available one:')
    exit_program(user_input)
    match user_input:
        case "1":
            df_count_by_cities = analysis.count_by_cities(df)
            print(df_count_by_cities)
            ask_for_visualize(df_count_by_cities, plot_title='Top accidents by city for 2016 - 2023')
            press_to_continue()
        case "2":
            user_year = checked_input('\nEnter the year')
            user_year = check_year(user_year)
            df_count_by_cities = analysis.count_by_cities_years(df, year=user_year)
            print(df_count_by_cities)
            ask_for_visualize(df_count_by_cities, plot_title=f'Top accidets by city for {user_year} year')
            press_to_continue()
        case "3":
            user_city = checked_input('\nEnter the city name')
            user_city = check_city(df, user_city)
            df_city_accidents_count_by_year = analysis.city_accidents_count_by_year(df, city=user_city)
            print(df_city_accidents_count_by_year)
            ask_for_visualize(df_city_accidents_count_by_year, chart_type='line', plot_title=f'Count of accidents for the {user_city}, split by year')
            press_to_continue()
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