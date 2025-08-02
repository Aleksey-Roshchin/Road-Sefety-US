import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.interface.user_interface as ui
from datetime import datetime
from src.constants import PROGRAM_LOGO

def main():
    ui.clear()
    ui.print_logo_centered(PROGRAM_LOGO)
    ui.main_menu()
    

if __name__ == "__main__":
    main()