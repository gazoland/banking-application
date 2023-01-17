import requests
import json
import os

from client.clients.src.client_account import AccountMenu
from client.clients.src.client_clients import ClientsMenu
from client.clients.src.client_cards import CardsMenu

class LoginMenu:
    def __init__(self, token, client_id, account_id, balance, pronoun, name, email, phone, username):
        self.token = token
        self.client_id = client_id
        self.account_id = account_id
        self.balance = balance
        self.pronoun = pronoun
        self.name = name
        self.email = email
        self.phone = phone
        self.username = username

    def menu(self) -> bool:
        print(f"Welcome back {self.pronoun} {self.name}. \n"
              f"Your current balance is $ {self.balance}.")
        command = ""
        while command not in [str(x) for x in range(1, 4)] and command != "e":
            print("Please select one of the options: \n"
                  "[1] Account\n"
                  "[2] Personal Information\n"
                  "[3] Cards\n"
                  "Or Press [E] to exit: ")
            command = input().lower()
        if command == "e":
            return False
        functions = {
            "1": AccountMenu(
                personal_token=self.token,
                account_id=self.account_id,
                balance=self.balance
            ),
            "2": ClientsMenu(
                personal_token=self.token,
                client_id=self.client_id,
                pronoun=self.pronoun,
                username=self.username,
                email=self.email,
                phone=self.phone
            ),
            "3": CardsMenu(
                personal_token=self.token,
                account_id=self.account_id,
                balance=self.balance
            )
        }
        functions[command].execute()
        self.username = functions["2"].username
        self.email = functions["2"].email
        self.phone = functions["2"].phone
        self.pronoun = functions["2"].pronoun
        if command in ["1", "3"]:
            self.balance = functions[command].balance
        return True

    def execute(self):
        no_exit = True
        while no_exit:
            no_exit = self.menu()


class InactiveAccount:
    def __init__(self, pronoun, name):
        self.pronoun = pronoun
        self.name = name

    def menu(self):
        print(f"Welcome back {self.pronoun} {self.name}. \n"
              f"Your account is currently closed.\n")
        no_exit = input("Please press [E] to exit: ").lower()
        if no_exit == "e":
            return False
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
            url="http://127.0.0.1:5000/v1/login",  # os.environ.get("BANK_URL") + "/v1/login",
            data={"username": username, "pwd": pwd}
        )
        return resp
