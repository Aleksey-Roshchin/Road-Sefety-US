import os, time, shutil, sys
import pandas as pd
from src.constants import SRC_PATH, README_PATH, USER_INPUT_FORM, EXIT_COMMANDS, BACK_COMMANDS, CSV
import src.visualization as visualization
import src.analysis as analysis
import src.stats as stats
import sys
from tabulate import tabulate


MENUS_PATH = SRC_PATH + r'/interface/menus'
PROGRAM_LOGO = MENUS_PATH + r"/program_logo.txt"
MAIN_MENU = MENUS_PATH + r'/main_menu.txt'
MAIN_MENU_LOGO = MAIN_MENU.rstrip('.txt') + '_logo.txt'
PRESET_REPORTS_MENU = MENUS_PATH + r'/preset_reports_menu.txt'
PRESET_REPORTS_LOGO = PRESET_REPORTS_MENU.rstrip('.txt') + '_logo.txt'
# CUSTOM_REPORTS_MENU = MENUS_PATH + r'/custom_reports_menu.txt'
# CUSTOM_REPORTS_LOGO = CUSTOM_REPORTS_MENU.rstrip('.txt') + '_logo.txt'
KPI_BY_YEAR_MENU = MENUS_PATH + r'/kpi_by_year_menu.txt'
KPI_BY_YEAR_LOGO = KPI_BY_YEAR_MENU.rstrip('.txt') + '_logo.txt'


MENU_HIERACHY = {
    PRESET_REPORTS_MENU: MAIN_MENU,
}

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


def press_to_continue(next_action, df):
    try:
        input('\nPress Enter to continue')
    except (KeyboardInterrupt, EOFError):
        print('\nExit requested')
        return
    next_action(df)

def exit_program(user_input: str) -> None:
    if user_input.strip().lower() in EXIT_COMMANDS:
        print("\nExiting program...\n")
        time.sleep(1)
        exit()

def checked_input(message='', df=None, current_menu=None, parent_menu=None) -> str:
    if message:
        print(message)
    user_input = input(USER_INPUT_FORM).lower().strip()
    exit_program(user_input)    # Check if user entered exit commands
    if user_input in BACK_COMMANDS:     # Check if user entered back commands
        if parent_menu:
            return parent_menu(df)
        else:
            print('\nAlready in the top menu.\n')
            time.sleep(1)
            return current_menu(df)
    return user_input


def print_centered(text: str) -> None:
    width = shutil.get_terminal_size().columns
    padding = (width - len(text)) // 2
    print(" " * max(padding, 0) + text, end='')

def filepath_check(filepath: str) -> None:
    try:
        with open(filepath, encoding='utf-8') as _:
            return None
    except FileNotFoundError:
        print(f'File {filepath} not found.\nPlease check the file name.')
        exit()

def print_logo(filepath: str) -> None:
    filepath_check(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())

def print_logo_centered(filepath: str) -> None:
    filepath_check(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for row in f.read().splitlines():
            print_centered(row)
            time.sleep(0.02)
            print()
        time.sleep(0.02)

def print_menu(filepath: str, is_parent_menu=False) -> None:
    filepath_check(filepath)
    clear()
    if is_parent_menu:
        print_logo(MENU_HIERACHY[filepath].rstrip('.txt') + '_logo.txt')
    print_logo(filepath.rstrip('.txt') + '_logo.txt')
    with open(filepath, 'r') as f:
        print(f.read())

def ask_for_visualize(df, df_original=None, parent_menu=None, plot_title=None, chart_type='bar') -> None:
    user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\n2. No', df_original, parent_menu=parent_menu).lower()
    while user_input not in ("1", "y", "yes", '2', 'no', 'n'):
        print(f'\nYou entered {user_input} which is not an option! Please re-enter')
        time.sleep(1)
        user_input = checked_input('\nDo you want to plot this table?\n\n1. Yes\n2. No').lower()
    match user_input:
        case "1" | "y" | "yes":
            x_col, y_col = list(df.columns)[:2]
            match chart_type:
                case 'bar':
                    visualization.bar_plot(df, x_col, y_col, plot_title=plot_title)
                case 'line':
                    visualization.line_plot(df, x_col, y_col, plot_title=plot_title)
        case '2' | 'no' | 'n':
            pass

# def check_year(year: str) -> int:
def check_year(year: str) -> pd.Timestamp:
    valid_years = [str(y) for y in range(2016, 2024)]
    min_year = min(valid_years)
    max_year = max(valid_years)
    while year not in valid_years:
        year = checked_input(f'Not an option! Please, choose the year from {min_year} to {max_year}')
    return pd.to_datetime(year).year
# return int(year)


def check_city(df: pd.DataFrame, city: str) -> str:
    valid_cities = df['City'].str.lower().unique()
    city = city.lower()
    while city not in valid_cities:
        city = checked_input(f'The data base has no this city. Please, check the city name.')
    return city

# Menus

def main_menu(df: pd.DataFrame, menu_filepath=MAIN_MENU) -> None:
    print_menu(menu_filepath)
    user_input = checked_input('\nChoose the available one:', df, current_menu=main_menu)
    exit_program(user_input)
    match user_input:
        case "1":
            preset_reports_menu(df)
        case "2":
            kpi_by_year_menu(df)
            press_to_continue(kpi_by_year_menu, df)
        case "3":
            stats.chi2_bulk_severe_vs_common_factors(df)
            press_to_continue(main_menu, df)
            return
        case "4":
            analysis.correlation_overview(df)
            press_to_continue(preset_reports_menu,df)
            return
        case "5":
            clear()
            with open(README_PATH, 'r', encoding='utf-8') as f: 
                print(f.read())
            press_to_continue(main_menu, df)
            return
        case _:
            print('\nNot an option!')
            time.sleep(1)
            main_menu(df)


def preset_reports_menu(df: pd.DataFrame, menu_filepath=PRESET_REPORTS_MENU):
    print_menu(menu_filepath)
    user_input = checked_input('\nChoose the available one:', df, current_menu=preset_reports_menu, parent_menu=main_menu)
    match user_input:
        case "1":
            df_count_by_cities = analysis.count_by_cities(df)
            print(tabulate(df_count_by_cities, headers='keys', tablefmt='pretty'))
            ask_for_visualize(df_count_by_cities, plot_title='Top accidents by city for 2016 - 2023', df_original=df, parent_menu=preset_reports_menu)
            press_to_continue(preset_reports_menu, df)
            return
        case "2":
            user_year = checked_input('\nEnter the year', df, parent_menu=preset_reports_menu)
            user_year = check_year(user_year)
            df_count_by_cities = analysis.count_by_cities_years(df, year=user_year)
            print(tabulate(df_count_by_cities, headers='keys', tablefmt='pretty'))
            ask_for_visualize(df_count_by_cities, plot_title=f'Top accidets by city for {user_year} year', df_original=df, parent_menu=preset_reports_menu)
            press_to_continue(preset_reports_menu, df)
            return
        case "3":
            user_city = checked_input('\nEnter the city name', df, parent_menu=preset_reports_menu)
            user_city = check_city(df, user_city)
            df_city_accidents_count_by_year = analysis.city_accidents_count_by_year(df, city=user_city)
            print(tabulate(df_city_accidents_count_by_year, headers='keys', tablefmt='pretty'))
            ask_for_visualize(df_city_accidents_count_by_year, chart_type='line', plot_title=f'Count of accidents for the {user_city}, split by year')
            press_to_continue(preset_reports_menu, df)
            return
        case "4":
            user_city = checked_input('\nEnter the city name', df, parent_menu=preset_reports_menu)
            user_city = check_city(df, user_city)
            user_year = checked_input('\nEnter the year', df, parent_menu=preset_reports_menu)
            user_year = check_year(user_year)
            user_num_rows = int(checked_input('\nHow many top results would you like to display?', df, parent_menu=preset_reports_menu))
            df_city_dangerous_streets = analysis.city_dangerous_streets(df, city=user_city, year=user_year, num_rows=user_num_rows)
            print(tabulate(df_city_dangerous_streets, headers='keys', tablefmt='pretty'))
            ask_for_visualize(df_city_dangerous_streets)
            press_to_continue(preset_reports_menu, df)
            return
        case _:
            print('\nNot an option!')
            time.sleep(1)
            preset_reports_menu(df)


# def custom_report_menu(df: pd.DataFrame, menu_filepath=CUSTOM_REPORTS_MENU, parent_menu=main_menu):
#     print_menu(menu_filepath)
#     user_input = checked_input('\nChoose the available one:', df, current_menu=preset_reports_menu, parent_menu=parent_menu)
#     match user_input:
#         case "1":
#             kpi_by_year_menu(df)
#             press_to_continue(custom_report_menu, df)
#             return
#         case _:
#             print('\nNot an option!')
#             time.sleep(1)
#             custom_report_menu(df)


# def kpi_by_year_menu(df: pd.DataFrame, menu_filepath=KPI_BY_YEAR_MENU, parent_menu=main_menu):

#     df_full = ld(CSV)
#     df_full = base_preprocess_datetime(df_full)
#     df_full = analysis.feat(df_full)
#     df = df_full

#     # need = {
#     #     "is_severe", "is_weekend", "is_night", "is_rush_hour",
#     #     "has_precipitation", "has_bad_weather", "is_visibility_low",
#     #     "is_freezing", "has_bump", "has_crossing", "road_type", "wind_speed_bin",
#     # }
#     # if not need.issubset(df.columns):
#     #     df = analysis.feat(df)

#     print_menu(menu_filepath, is_parent_menu=True)
#     choice = checked_input("\nChoose KPI (1-7): ", df, parent_menu=parent_menu).strip()

#     metric_map = {
#         "2": "accidents",
#         "3": "severe_share",
#         "4": "avg_severity",
#         "5": "weekend_share",
#         "6": "precip_share",
#         "7": "bad_weather_share",
#     }

#     df_filtered = choose_period_df(df)
#     if df_filtered.empty:
#         print("\n[Notice] No data left after filtering. Showing all years.")
#         df_filtered = df

#     if choice == "1":
#         df_stack = analysis.kpi_components_by_year(df_filtered, scale=10000)
#         pretty = df_stack.rename(columns={
#             "severe": "Severe",
#             "weekend_only": "Weekend only",
#             "precip_only": "Precip only",
#             "bad_only": "Bad weather only",
#             "other": "Other",
#         })

#         visualization.stacked_components_bar(
#             pretty,
#             x_col="year",
#             stack_cols=("Severe", "Weekend only", "Precip only", "Bad weather only", "Other"),
#             title="Accidents by year (stacked components, per 10k)",
#             ylabel="Accidents (per 10k)"
#         )

#         print(pretty[["year", "accidents"]].rename(columns={"accidents": "Accidents (per 10k)"}))

#         press_to_continue(main_menu,df)
#         return

#     metric = metric_map.get(choice, "accidents")
#     df_kpi = analysis.kpi_by_year(df_filtered, metric)
#     print(df_kpi)
#     if len(df_kpi.columns) == 2:
#         ask_for_visualize(df_kpi, df, parent_menu)

#     press_to_continue(main_menu,df)


def start_from_input(s: str):
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


def end_exclusive_from_input(s: str):
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


def choose_kpi(df, menu_filepath=KPI_BY_YEAR_MENU, parent_menu=main_menu) -> str:
    # print("\nCustom reports")
    # print("1. All metrics (stacked, per 10k)")
    # print("2. Accidents (count)")
    # print("3. Severe share (%)")
    # print("4. Avg Severity")
    # print("5. Weekend share (%)")
    # print("6. Precipitation share (%)")
    # print("7. Bad weather share (%)")
    # print("8. Accidents by month")
    # print("9. Night share (%)")
    # print("10. Rush hour share (%)")
    # print("11. Low visibility share (%)")
    # print("12. Freezing share (%)")
    # print("13. Bump share (%)")
    # print("14. Crossing share (%)")
    # print("15. DUI signal share (%)")
    print_menu(menu_filepath)
    choice = checked_input("\nChoose KPI (1-15): ", df=df, parent_menu=parent_menu).strip()
    return {
        "1": "__stacked__",
        "2": "accidents",
        "3": "severe_share",
        "4": "avg_severity",
        "5": "weekend_share",
        "6": "precip_share",
        "7": "bad_weather_share",
        "8": "accidents_by_month",
        "9": "night_share",
        "10": "rush_hour_share",
        "11": "visibility_low_share",
        "12": "freezing_share",
        "13": "bump_share",
        "14": "crossing_share",
        "15": "dui_share",
    }.get(choice, "accidents")

def kpi_by_year_menu(df: pd.DataFrame, menu_filepath=KPI_BY_YEAR_MENU, parent_menu=main_menu) -> pd.DataFrame:
    metric = choose_kpi(df, menu_filepath=KPI_BY_YEAR_MENU, parent_menu=main_menu)

    d_period = choose_period_df(df)
    if d_period.empty:
        print("\n[Notice] No data left after filtering. Showing all years.")
        d_period = df

    d = analysis.ensure_features(df)

    if "Start_Time" in d.columns and pd.api.types.is_datetime64_any_dtype(d["Start_Time"]):
        times = d["Start_Time"]
    else:
        times = pd.to_datetime(d["Start_Time"], errors="coerce")

    if d_period is not df:
        _t = pd.to_datetime(df["Start_Time"], errors="coerce")
        mask_src = df.index[_t.isin(pd.to_datetime(d_period["Start_Time"], errors="coerce"))]
        mask = d.index.isin(mask_src)
        d_filtered = d.loc[mask]
    else:
        d_filtered = d

    if metric == "__stacked__":
        pretty = (
            analysis.kpi_components_by_year(d_filtered, scale=10000)
            .rename(
                columns={
                    "severe": "Severe",
                    "weekend_only": "Weekend only",
                    "precip_only": "Precip only",
                    "bad_only": "Bad weather only",
                    "night_only": "Night only",
                    "rush_hour_only": "Rush hour only",
                    "visibility_low_only": "Low visibility only",
                    "freezing_only": "Freezing only",
                    "bump_only": "Bump only",
                    "crossing_only": "Crossing only",
                    "dui_only": "DUI only",
                    "other": "Other",
                }
            )
        )
        visualization.stacked_components_bar(
            pretty,
            x_col="year",
            stack_cols=(
                "Severe",
                "Weekend only",
                "Precip only",
                "Bad weather only",
                "Night only",
                "Rush hour only",
                "Low visibility only",
                "Freezing only",
                "Bump only",
                "Crossing only",
                "DUI only",
                "Other",
            ),
            title="Accidents by year (stacked components, per 10k)",
            ylabel="Accidents (per 10k)",
        )
        print(pretty[["year", "accidents"]].rename(columns={"accidents": "Accidents (per 10k)"}))
        return d

    if metric == "accidents_by_month":
        df_month = analysis.accidents_by_month(d_filtered)
        print(df_month)
        ask_for_visualize(df_month)
        return d

    df_kpi = analysis.kpi_by_year(d_filtered, metric)
    print(df_kpi)
    if len(df_kpi.columns) == 2:
        ask_for_visualize(df_kpi)

    return d

def choose_period_df(df: pd.DataFrame, parent_menu=kpi_by_year_menu) -> pd.DataFrame:
    print("\nWhich period do you want to show?")
    print("1. All years")
    print("2. Specific year")
    print("3. Specific date range")
    choice = checked_input("\nYour choice (1-3): ", df, parent_menu=parent_menu).strip()

    if choice == "1":
        return df

    if choice == "2":
        y = checked_input("Enter year (2016-2023): ", df, parent_menu=parent_menu).strip()
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
            s_from = checked_input("From date: ", df, parent_menu=parent_menu).strip()
            s_to = checked_input("To date: ", df, parent_menu=parent_menu).strip()
            dt_from = start_from_input(s_from)
            dt_to_excl = end_exclusive_from_input(s_to)
            if (dt_from is not None) and (dt_to_excl is not None) and (dt_from < dt_to_excl):
                tmp = (df["Start_Time"] if pd.api.types.is_datetime64_any_dtype(df["Start_Time"])
                       else pd.to_datetime(df["Start_Time"], errors="coerce"))
                mask = (tmp >= dt_from) & (tmp < dt_to_excl)
                return df[mask]
            print("Could not parse the dates — please try again.")
        print("Showing all years.")
        return df

    print("No such option. Showing all years.")
    return df


def help():
    pass