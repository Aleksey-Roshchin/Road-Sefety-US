import os, time, shutil

# Consts
MENUS = 'interface/menus/'
USER_INPUT_FORM = "\n\n>>> "

# Utils
def clear():
    os.system('clear')

def print_centered(text):
    width = shutil.get_terminal_size().columns
    padding = (width - len(text)) // 2
    print(" " * max(padding, 0) + text, end='')

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
    print_logo(filepath.rstrip('.txt') + '_logo.txt')
    with open(filepath, 'r') as f:
        print(f.read())



# Menus

def main_menu():
    clear()
    print_menu(MENUS + 'main.txt')
