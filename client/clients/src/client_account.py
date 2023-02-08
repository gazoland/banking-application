import requests
import os
import json

import resources


class AccountMenu:
    def __init__(self, personal_token, account_id, balance):
        self.token = personal_token
        self.account_id = account_id
        self.balance = balance
        self.url = "http://127.0.0.1:5000/v1/accounts"  # os.environ.get("BANK_URL") + "/v1/accounts"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.endpoints = {
            "1": "/deposit",
            "2": "/withdraw",
            "3": "/transfer",
            "4": "/statement"
        }

    def __str__(self):
        return "------------------- My Account -------------------\n"

    def menu(self):
        command = ""
        while command not in [str(x) for x in range(1, len(self.endpoints.keys()) + 1)] and command != "b":
            print(f"Your current balance is ${self.balance}")
            print("What would you like to do?\n"
                  "[1] Deposit\n"
                  "[2] Withdraw\n"
                  "[3] Transfer\n"
                  "[4] View Statement\n"
                  "Or press [B] to go back to the main menu: ")
            command = input().lower()
        if command == "b":
            return False
        elif command == "1":
            self.deposit(self.url + self.endpoints[command])
        elif command == "2":
            self.withdraw(self.url + self.endpoints[command])
        elif command == "3":
            self.transfer(self.url + self.endpoints[command])
        elif command == "4":
            self.get_statement(self.url + self.endpoints[command])

        return True

    def deposit(self, request_url):
        while True:
            print(f"Your current balance is ${self.balance}")
            amount = input("Type the amount you would like to deposit or [B] to go back: ")
            if amount in ["b", "B"]:
                return

            amount_check = resources.valid_amount_check(amount)
            if not amount_check.valid:
                print(amount_check.message)
                continue

            float_amount = float(amount)

            resp = self.__amount_handling_request(float_amount, request_url)
            if resp.status_code == 200:
                print(f"You deposited ${float_amount} into your account.")
                self.balance += float_amount
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Invalid amount to deposit. Amount should be between $0.01 and $5,000.00")
            else:
                print("There was an error. Please try again later.")

    def transfer(self, request_url):
        while True:
            print(f"Your current balance is ${self.balance}")
            amount = input("Type the amount you would like to transfer or [B] to go back: ")
            if amount in ["b", "B"]:
                return

            amount_check = resources.valid_amount_check(amount)
            if not amount_check.valid:
                print(amount_check.message)
                continue

            float_amount = float(amount)

            recipient_email = input("Type the email of the person you would like to transfer to or [B] to go back: ")
            if amount in ["b", "B"]:
                return

            check_email_recipient = self.__get_name_from_email_request(float_amount, recipient_email, request_url)
            if check_email_recipient.status_code == 400:
                print("This email is not registered to receive transfers.")
                continue
            recipient_name = json.loads(check_email_recipient.text)["data"]["full_name"]

            confirm_transfer = 'X'
            while confirm_transfer not in ("b", "y"):
                confirm_transfer = input(f"Transferring ${float_amount} to {recipient_name}.\n"
                                         f"Press [Y] to confirm or [B] to go back: ").lower()
                if confirm_transfer == "b":
                    break
                elif confirm_transfer == "y":
                    resp = self.__transfer_request(float_amount, recipient_email, request_url)
                    if resp.status_code == 200:
                        print(f"You sent ${float_amount} to {recipient_name}.")
                        self.balance -= float_amount
                        return
                    elif resp.status_code == 400:
                        print("Recipient email is invalid.")
                    elif resp.status_code == 401:
                        print("Token authentication failed.")
                    elif resp.status_code == 403:
                        print("Insufficient funds.")
                    elif resp.status_code == 409:
                        print("Invalid amount to transfer. Amount should be between $0.01 and $10,000.00")
                    else:
                        print("There was an error. Please try again later.")


    def withdraw(self, request_url):
        while True:
            print(f"Your current balance is ${self.balance}")
            amount = input("Type the amount you would like to withdraw or [B] to go back: ")
            if amount in ["b", "B"]:
                return

            amount_check = resources.valid_amount_check(amount)
            if not amount_check.valid:
                print(amount_check.message)
                continue

            float_amount = float(amount)

            resp = self.__amount_handling_request(float_amount, request_url)
            if resp.status_code == 200:
                print(f"Withdrawing ${float_amount} from your account: Success!\n"
                      f"Please take the money from the cash dispenser.")
                self.balance -= float_amount
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 403:
                print("Insufficient funds.")
            elif resp.status_code == 409:
                print("Invalid amount to withdraw. Amount should be between $0.01 and $1,000.00")
            else:
                print("There was an error. Please try again later.")

    def get_statement(self, request_url):
        resp = self.__statement_request(request_url)
        if resp.status_code == 200:
            for transaction in json.loads(resp.text)["data"]["transactions"]:
                print(transaction)
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")
        return

    def execute(self):
        no_exit = True
        while no_exit:
            print(self)
            no_exit = self.menu()

    def __amount_handling_request(self, amount, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"amount": amount,
                                                                                "account_id": self.account_id})
        return resp

    def __get_name_from_email_request(self, amount, destination_email, request_url):
        val = requests.request("GET", request_url, headers=self.headers, data={"amount": amount,
                                                                               "destination_email": destination_email,
                                                                               "account_id": self.account_id})
        return val

    def __transfer_request(self, amount, destination_email, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"amount": amount,
                                                                                "destination_email": destination_email,
                                                                                "account_id": self.account_id})
        return resp

    def __statement_request(self, request_url):
        statement = requests.request("GET", request_url, headers=self.headers, data={"account_id": self.account_id})
        return statement
