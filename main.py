import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.interface.user_interface as ui
import time
from datetime import datetime
from src.constants import PROGRAM_LOGO

def main():
    ui.clear()
    ui.print_logo_centered(PROGRAM_LOGO)
    choice = ui.main_menu()
    match choice:
        case "1":
            pass
        case "2":
            pass
        case "3":
            pass
        case _:
            print('\nNot an option!')
            time.sleep(1)
            main()

if __name__ == "__main__":
    main()