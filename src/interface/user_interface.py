import pandas as pd
import os, time, shutil
from pathlib import Path
from src.constants import SRC_PATH, USER_INPUT_FORM, EXIT_COMMANDS
import src.visualization as visualization
import src.analysis as analysis
import sys

# Consts
MENUS_PATH = SRC_PATH + r'/interface/menus'
PROGRAM_LOGO = MENUS_PATH + r"/program_logo.txt"
MAIN_MENU = MENUS_PATH + r'/main_menu.txt'
MAIN_MENU_LOGO = MAIN_MENU.rstrip('.txt') + '_logo.txt'
PRESET_REPORTS_MENU = MENUS_PATH + r'/preset_reports_menu.txt'
PRESET_REPORTS_LOGO = PRESET_REPORTS_MENU.rstrip('.txt') + '_logo.txt'
KPI_BY_YEAR_MENU = MENUS_PATH + r'/kpi_by_year_menu.txt'
KPI_BY_YEAR_LOGO = KPI_BY_YEAR_MENU.rstrip('.txt') + '_logo.txt'


# Utils
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def enable_utf8():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if os.name == 'nt':
        os.system('chcp 65001 > nul')

def press_to_continue(df=None):
    while True:
        print("\nWhat do you want to do next?")
        print("1. Return to main menu")
        print("2. Exit program")
        choice = input("Your choice (1-2): ").strip().lower()

        if choice in ("1", "menu", "m", "y", "yes"):
            if df is not None:
                main_menu(df)
            return
        if choice in ("2", "exit", "e", "q", "n", "no"):
            print("\nExit\n")
            time.sleep(1)
            exit()

        print("Invalid option. Please choose 1 or 2.")



def exit_program(user_input: str) -> None:
    if user_input.strip().lower() in EXIT_COMMANDS:
        print("\nExiting program...\n")
        time.sleep(1)
        exit()


def checked_input(message=''):
    if message:
        print(message)
    user_input = input(USER_INPUT_FORM)
    exit_program(user_input)
    return user_input


def print_centered(text: str) -> None:
    width = shutil.get_terminal_size().columns
    padding = (width - len(text)) // 2
    print(" " * max(padding, 0) + text, end='')


def filepath_check(filepath):
    try:
        with open(filepath, encoding='utf-8') as f:
            return None
    except FileNotFoundError:
        print(f'File {filepath} not found.\nPlease check the file name.')
        exit()


def print_logo(filepath):
    filepath_check(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())



def print_logo_centered(filepath):
    filepath_check(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for row in f.read().splitlines():
            print_centered(row)
            time.sleep(0.1)
            print()
        time.sleep(1)


def print_menu(filepath):
    filepath_check(filepath)
    clear()
    print_logo(filepath.rstrip('.txt') + '_logo.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())



def ask_for_visualize(df):
    user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\2. No').lower()
    while user_input not in ("1", "y", "yes", '2', 'no', 'n'):
        print(f'\nYou entered {user_input} which is not an option! Please re-enter')
        time.sleep(1)
        user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\n2. No').lower()
    match user_input:
        case "1" | "y" | "yes":
            x_col, y_col = df.columns
            visualization.bar_plot(df, x_col, y_col)
        case '2' | 'no' | 'n':
            pass


# Menus

def main_menu(df):
    print_menu(MAIN_MENU)
    user_input = checked_input('\nChoose the available one:')
    exit_program(user_input)
    match user_input:
        case "1":
            preset_reports_menu(df)
        case "2":
            kpi_by_year_menu(df)
        case "3":
            pass
        case "4":
            analysis.correlation_overview(df)  # NEW
            press_to_continue(df)
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
            ask_for_visualize(df_count_by_cities)
            press_to_continue(df)
        case "2":
            kpi_by_year_menu(df)
        case "3":
            pass
        case "4":
            pass
        case _:
            print('\nNot an option!')
            time.sleep(1)
            preset_reports_menu(df)



def kpi_by_year_menu(df: pd.DataFrame):
    print_menu(KPI_BY_YEAR_MENU)
    choice = checked_input("\nChoose KPI (1-7): ").strip()

    metric_map = {
        "2": "accidents",
        "3": "severe_share",
        "4": "avg_severity",
        "5": "weekend_share",
        "6": "precip_share",
        "7": "bad_weather_share",
    }

    df_filtered = _choose_period_df(df)
    if df_filtered.empty:
        print("\n[Notice] No data left after filtering. Showing all years.")
        df_filtered = df

    if choice == "1":
        df_stack = analysis.kpi_components_by_year(df_filtered, scale=10000)
        pretty = df_stack.rename(columns={
            "severe": "Severe",
            "weekend_only": "Weekend only",
            "precip_only": "Precip only",
            "bad_only": "Bad weather only",
            "other": "Other",
        })

        visualization.stacked_components_bar(
            pretty,
            x_col="year",
            stack_cols=("Severe", "Weekend only", "Precip only", "Bad weather only", "Other"),
            title="Accidents by year (stacked components, per 10k)",
            ylabel="Accidents (per 10k)"
        )

        print(pretty[["year", "accidents"]].rename(columns={"accidents": "Accidents (per 10k)"}))

        press_to_continue(df)
        return

    metric = metric_map.get(choice, "accidents")
    df_kpi = analysis.kpi_by_year(df_filtered, metric)
    print(df_kpi)
    if len(df_kpi.columns) == 2:
        ask_for_visualize(df_kpi)

    press_to_continue(df)

def _start_from_input(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        if len(s) == 4 and s.isdigit():
            return pd.to_datetime(f"{s}-01-01", errors="coerce")
        if len(s) == 7 and s[4] == "-":
            return pd.to_datetime(f"{s}-01", errors="coerce")
        return pd.to_datetime(s, errors="coerce")
    except Exception:
        return None

def _end_exclusive_from_input(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        if len(s) == 4 and s.isdigit():
            base = pd.to_datetime(f"{s}-01-01", errors="coerce")
            return base + pd.DateOffset(years=1)
        if len(s) == 7 and s[4] == "-":
            base = pd.to_datetime(f"{s}-01", errors="coerce")
            return base + pd.DateOffset(months=1)
        base = pd.to_datetime(s, errors="coerce")
        if pd.isna(base):
            return None
        return base + pd.DateOffset(days=1)
    except Exception:
        return None

def _choose_period_df(df: pd.DataFrame) -> pd.DataFrame:
    print("\nWhich period do you want to show?")
    print("1. All years")
    print("2. Specific year")
    print("3. Specific date range")
    choice = checked_input("\nYour choice (1-3): ").strip()

    if choice == "1":
        return df

    if choice == "2":
        y = checked_input("Enter year (2016-2022): ").strip()
        if len(y) == 4 and y.isdigit():
            year = int(y)
            if "year" in df.columns:
                return df[df["year"] == year]
            years = pd.to_datetime(df["Start_Time"], errors="coerce").dt.year
            return df[years == year]
        print("Invalid year format. Showing all years.")
        return df

    if choice == "3":
        for _ in range(2):
            print("\nExamples of valid input: 2020  |  2020-05  |  2020-05-10")
            s_from = checked_input("From date: ").strip()
            s_to   = checked_input("To date: ").strip()
            dt_from = _start_from_input(s_from)
            dt_to_excl = _end_exclusive_from_input(s_to)
            if (dt_from is not None) and (dt_to_excl is not None) and (dt_from < dt_to_excl):
                tmp = pd.to_datetime(df["Start_Time"], errors="coerce") if not pd.api.types.is_datetime64_any_dtype(df["Start_Time"]) else df["Start_Time"]
                mask = (tmp >= dt_from) & (tmp < dt_to_excl)
                return df[mask]
            print("Could not parse the dates — please try again.")
        print("Showing all years.")
        return df

    print("No such option. Showing all years.")
    return df



def custom_reports_menu():
    pass


def help():
    pass