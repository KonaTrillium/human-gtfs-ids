COLOR_RED   = "\033[1;31m"
COLOR_BLUE  = "\033[1;34m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0;0m"

def print_red(str):
    print(COLOR_RED + str + COLOR_RESET)

def print_blue(str):
    print(COLOR_BLUE + str + COLOR_RESET)

def print_green(str):
    print(COLOR_GREEN + str + COLOR_RESET)