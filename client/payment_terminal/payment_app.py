import os
import sys
sys.path.append(os.getcwd() + "/client")

from src.menu import Menu


def main():
    establishment = "WALMART 215965"
    location = "MIAMI FL"
    no_exit = True
    while no_exit:
        no_exit = Menu(establishment_code=establishment, location=location).menu()
    print("Exiting...")


if __name__ == "__main__":
    main()
