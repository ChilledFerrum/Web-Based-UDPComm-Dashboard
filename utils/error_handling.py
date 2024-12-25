# ANSI escape codes for colored output
RED = "\033[0;31m"
ORANGE = "\033[0;202m"
GREEN = "\033[0;32m"
WHITE = "\033[0;37m"

import sys

def kill_with_error(error_message, error_code=None):
    if error_code is not None:
        print(f"{RED}Error: {error_message} (Code: {error_code}){WHITE}")
    else:
        print(f"{RED}Error: {error_message}{WHITE}")
    sys.exit(1)

def throw_error(error_message, error_code=None):
    if error_code is not None:
        print(f"{ORANGE}Error: {error_message} (Code: {error_code}){WHITE}")
    else:
        print(f"{ORANGE}Error: {error_message}{WHITE}")