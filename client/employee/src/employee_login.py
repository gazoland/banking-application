import requests
import json
import os

from src.employee_clients import ClientsMenu
from src.employee_cards import CardRequestsMenu


class LoginMenu:
    def __init__(self, token, emp_id, name, email, username):
        self.token = token
        self.emp_id = emp_id
        self.name = name
        self.email = email
        self.username = username

    def menu(self) -> bool:
        print(f"Hello, {self.name}.")
        command = ""
        while command not in [str(x) for x in range(1, 3)] and command != "e":
            print("Please select one of the options: \n"
                  "[1] Clients\n"
                  "[2] Analyze Card Requests\n"
                  "Or Press [E] to exit: ")
            command = input().lower()

        if command == "e":
            return False

        functions = {
            "1": ClientsMenu(
                personal_token=self.token,
                emp_id=self.emp_id
            ),
            "2": CardRequestsMenu(
                emp_id=self.emp_id,
                personal_token=self.token
            )
        }
        functions[command].execute()
        return True

    def execute(self):
        no_exit = True
        while no_exit:
            no_exit = self.menu()


class Login:
    def login_attempt(self) -> tuple:
        print("Welcome to Bank X.\n"
              "Please enter your username and password.")
        user = input("Username: ")
        pwd = input("Password: ")
        resp = self.__login_request(user, pwd)
        if resp.status_code == 200:
            print("Login successful.")
            return True, json.loads(resp.text)["data"]
        elif resp.status_code == 400:
            print("Incorrect username/password. Try again.")
        elif resp.status_code == 401:
            print("Incorrect password. Try again.")
        else:
            print(resp.status_code, resp.text)
        return False, None

    @staticmethod
    def __login_request(username, pwd):
        resp = requests.request(
            method="POST",
            url="http://127.0.0.1:5000/v1/login/employee",  # os.environ.get("BANK_URL") + "/v1/login",
            data={"username": username, "pwd": pwd}
        )
        return resp
