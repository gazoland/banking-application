from src.purchase import PurchaseMenu


class Menu:
    def __init__(self, establishment_code, location):
        self.est_code = establishment_code
        self.est_location = location

    def menu(self) -> bool:
        print(f"\n{self.est_code}, {self.est_location}")
        command = ""
        while command not in [str(x) for x in range(1, 2)] and command != "e":
            print("Please select one of the options: \n"
                  "[1] New Purchase\n"
                  "Or Press [E] to exit: ")
            command = input().lower()

        if command == "e":
            return False

        functions = {
            "1": PurchaseMenu(est_code=self.est_code, location=self.est_location)
        }
        functions[command].menu()
        return True

    def execute(self):
        no_exit = True
        while no_exit:
            no_exit = self.menu()
