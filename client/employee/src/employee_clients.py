import requests
import os
import json

from client import resources

class ClientsMenu:
    def __init__(self, personal_token, emp_id):
        self.token = personal_token
        self.emp_id = emp_id
        self.client_account_active = None
        self.client_account_id = None
        self.client_username = None
        self.client_name = None
        self.client_account_balance = None
        self.url = "http://127.0.0.1:5000/v1/employee"  # os.environ.get("BANK_URL") + "/v1/employee"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.endpoints = {
            "1": "/clients/new",
            "2": "/cards/new_client_card",
            "3": "/accounts",
            "4": "/accounts/deposit",
            "5": "/accounts/withdraw"
        }

    def __str__(self):
        return "-------------------------- Clients --------------------------\n"

    def menu(self):
        command = ""
        while command not in [str(x) for x in range(1, len(self.endpoints.keys()) + 1)] and command != "b":
            print("What would you like to do?\n"
                  "[1] Register New Client\n"
                  "[2] New Client Card\n"
                  "[3] Close Client Account\n"
                  "[4] Make Deposit\n"
                  "[5] Make Withdrawal\n"
                  "Or press [B] to go back to the main menu: ")
            command = input().lower()
        if command == "b":
            return False
        elif command == "1":
            self.register_new_client(self.url + self.endpoints[command])
        elif command == "2":
            self.new_client_debit_card()
        elif command == "3":
            self.close_client_account(self.url + self.endpoints[command])
        elif command == "4":
            self.make_deposit(self.url + self.endpoints[command])
        elif command == "5":
            self.make_withdrawal(self.url + self.endpoints[command])
        return True

    def register_new_client(self, request_url):
        pronouns = {
            "1": "Mr.",
            "2": "Mrs.",
            "3": "Ms.",
            "4": "Miss",
            "5": "Mx.",
            "6": "Leave blank"
        }
        while True:
            print(f"Press [B] to go back at anytime.")
            # NAME
            client_name = input("Client's full name: ")
            if client_name in ["b", "B"]:
                return

            # PRONOUN
            pronoun_id = 'X'
            while pronoun_id not in pronouns.keys():
                for code, pronoun_name in pronouns.items():
                    print(f"[{code}] {pronoun_name}")
                pronoun_id = input("Select a new treatment pronoun or [B] to go back: ").lower()
                if pronoun_id == "b":
                    return
            pronoun = int(pronoun_id)

            # DOB
            while True:
                client_dob = input("Client's Date of Birth (MM/DD/YYYY): ").lower()
                if client_dob == "b":
                    return
                new_dob_check = resources.new_dob_check(client_dob)
                if new_dob_check.valid:
                    break
                print(new_dob_check.message)

            # EMAIL
            while True:
                client_email = input("Client's email: ")
                if client_email == "b":
                    return
                new_email_check = resources.new_email_check(client_email)
                if not new_email_check.valid:
                    print(new_email_check.message)
                    continue
                resp = self.__check_existing_email(client_email)
                valid_email = json.loads(resp.text)["data"]["valid_email"]
                if not valid_email:
                    print("This email is already taken. Please choose a new one.")
                    continue
                break

            # PHONE
            while True:
                client_phone = input("Client's phone: ").lower()
                if client_phone == "b":
                    return
                new_phone_check = resources.new_phone_check(client_phone)
                if not new_phone_check.valid:
                    print(new_phone_check.message)
                    continue
                resp = self.__check_existing_phone(client_phone)
                valid_phone = json.loads(resp.text)["data"]["valid_phone"]
                if not valid_phone:
                    print("This phone is already taken. Please choose a new one.")
                    continue
                break

            # USERNAME
            while True:
                client_username = input("Client's username: ")
                if client_username in ["b", "B"]:
                    return
                new_username_check = resources.new_username_check(client_username)
                if not new_username_check.valid:
                    print(new_username_check.message)
                    continue
                resp = self.__check_existing_username(client_username)
                valid_username = json.loads(resp.text)["data"]["valid_username"]
                if not valid_username:
                    print("This username is already taken. Please choose a new one.")
                    continue
                break

            # PWD
            while True:
                client_pwd = input("Client's password: ")
                if client_pwd in ["b", "B"]:
                    return
                new_pwd_check = resources.new_password_check(client_pwd)
                if new_pwd_check.valid:
                    confirm_pwd = input("Confirm password: ")
                    if client_pwd == confirm_pwd:
                        break
                    print("Passwords don't match.")
                    continue
                print(new_pwd_check.message)

            # INITIAL DEPOSIT
            while True:
                amount = input("Type the initial deposit amount or [B] to go back: ").lower()
                if amount == "b":
                    return

                amount_check = resources.valid_amount_check(amount)
                if not amount_check.valid:
                    print(amount_check.message)
                    continue
                break
            float_amount = float(amount)

            data = {
                "username": client_username,
                "full_name": client_name,
                "pwd": client_pwd,
                "email": client_email,
                "pronoun_id": pronoun,
                "dob": client_dob,
                "phone": client_phone,
                "deposit": float_amount
            }

            resp = self.__post_new_client(data, request_url)
            if resp.status_code == 200:
                print("Client created successfully.")
                self.client_account_id = json.loads(resp.text)["data"]["acc_id"]
                self.client_username = client_username
                return

            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print(json.loads(resp.text)["message"])
            else:
                print("There was an error. Please try again later.")

    def new_client_debit_card(self):
        if self.client_account_id is None:
            self.__init_client_info()
        while True:
            card_pin = input("Type your card PIN: ")
            if not card_pin.isdigit() or len(card_pin) != 4:
                print("Invalid PIN. Please type a 4-digit PIN.")
                continue
            break
        card_data = {
            "brand_id": 1,
            "category_id": 1,
            "card_type": "debit",
            "pin": card_pin,
            "account_id": self.client_account_id,
            "req_type": "new_client"
        }
        resp = self.__post_new_card(card_data)
        if resp.status_code == 200:
            print(f"Debit card created. Client username: {self.client_username}\n"
                  f"Card Activation Code: {json.loads(resp.text)['data']['activation_code']}")
            return
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")

    def close_client_account(self, request_url):
        if self.client_account_id is None:
            self.__init_client_info()
        self.__init_client_account_info()
        acc_status = "Open" if self.client_account_active else "Closed"

        print(f"Client: {self.client_name} - Remaining funds: ${self.client_account_balance}. "
              f"Account status: {acc_status}")
        confirm = input("Closing the account. Proceed? Press [Y] to confirm or any other key to go back: ").lower()
        if confirm != "y":
            return
        if not self.client_account_active:
            print("Account is already closed.")
            return

        if self.client_account_balance > 0:
            print("Withdrawing remaining funds...")
            resp = self.__amount_handling_request(self.client_account_balance, request_url + "/withdraw")
            if resp.status_code == 200:
                print("Withdrawal approved.")
                self.client_account_balance = 0
            elif resp.status_code == 401:
                print("Token authentication failed. Please login again.")
            else:
                print("There was an error. Please try again later.")
        print("Closing account...")
        resp = self.__close_account(request_url + "/close")
        if resp.status_code == 200:
            print("Account closed.")
            self.client_account_active = False
        elif resp.status_code == 401:
            print("Token authentication failed. Please login again.")
        else:
            print("There was an error. Please try again later.")

    def make_withdrawal(self, request_url):
        if self.client_account_id is None:
            self.__init_client_info()
        self.__init_client_account_info()
        while True:
            print(f"Client: {self.client_name} - Balance: ${self.client_account_balance}")
            amount = input("Type the amount you would like to withdraw or [B] to go back: ").lower()
            if amount == "b":
                return

            amount_check = resources.valid_amount_check(amount)
            if not amount_check.valid:
                print(amount_check.message)
                continue
            if float(amount) > self.client_account_balance:
                print("Insufficient funds.")
                continue

            float_amount = float(amount)

            resp = self.__amount_handling_request(float_amount, request_url)
            if resp.status_code == 200:
                print(f"Withdrawing ${float_amount}: Success!")
                self.client_account_balance -= float_amount
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 403:
                print("Insufficient funds.")
            elif resp.status_code == 409:
                print("Invalid amount to withdraw.")
            else:
                print("There was an error. Please try again later.")

    def make_deposit(self, request_url):
        if self.client_account_id is None:
            self.__init_client_info()
        self.__init_client_account_info()
        while True:
            print(f"Client: {self.client_name} - Balance: ${self.client_account_balance}")
            amount = input("Type the amount you would like to deposit or [B] to go back: ").lower()
            if amount == "b":
                return

            amount_check = resources.valid_amount_check(amount)
            if not amount_check.valid:
                print(amount_check.message)
                continue

            float_amount = float(amount)

            resp = self.__amount_handling_request(float_amount, request_url)
            if resp.status_code == 200:
                print(f"Depositing ${float_amount}: Success!")
                self.client_account_balance += float_amount
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Invalid amount to deposit.")
            else:
                print("There was an error. Please try again later.")

    def execute(self):
        no_exit = True
        while no_exit:
            print(self)
            no_exit = self.menu()

    def __init_client_info(self):
        while True:
            client_phone = input("Type client's phone or [B] to go back: ").lower()
            if client_phone == "b":
                return
            resp = self.__get_client_account_id(client_phone)
            if resp.status_code == 200:
                self.client_account_id = json.loads(resp.text)["data"]["acc_id"]
                return
            print(json.loads(resp.text)["message"])

    def __init_client_account_info(self):
        resp = self.__get_client_account_info()
        if resp.status_code == 200:
            data = json.loads(resp.text)["data"]
            self.client_name = data["full_name"]
            self.client_account_active = data["active"]
            self.client_account_balance = float(data["balance"])
            return

        print(json.loads(resp.text)["message"])

    def __check_existing_username(self, new_username):
        resp = requests.request("GET", "http://127.0.0.1:5000/v1/clients/username", headers=self.headers, data={
            "new_value": new_username,
            "old_value": "NULL",
            "client_id": 1,
            "emp_id": self.emp_id})
        return resp

    def __check_existing_email(self, new_email):
        resp = requests.request("GET", "http://127.0.0.1:5000/v1/clients/email", headers=self.headers, data={
            "new_value": new_email,
            "old_value": "NULL",
            "client_id": 1,
            "emp_id": self.emp_id})
        return resp

    def __check_existing_phone(self, new_phone):
        resp = requests.request("GET", "http://127.0.0.1:5000/v1/clients/phone", headers=self.headers, data={
            "new_value": new_phone,
            "old_value": "NULL",
            "client_id": 1,
            "emp_id": self.emp_id})
        return resp

    def __get_client_account_id(self, phone):
        resp = requests.request("GET", self.url + "/accounts/id", headers=self.headers, data={
            "phone": phone,
            "emp_id": self.emp_id})
        return resp

    def __get_client_account_info(self):
        resp = requests.request("GET", self.url + "/accounts/info", headers=self.headers, data={
            "account_id": self.client_account_id,
            "emp_id": self.emp_id})
        return resp

    def __post_new_client(self, data, request_url):
        data["emp_id"] = self.emp_id
        resp = requests.request("POST", request_url, headers=self.headers, data=data)
        return resp

    def __post_new_card(self, data):
        data["emp_id"] = self.emp_id
        resp = requests.request("POST", self.url + "/cards/new_client_card", headers=self.headers,
                                data=data)
        return resp

    def __amount_handling_request(self, amount, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"amount": amount,
                                                                                "account_id": self.client_account_id,
                                                                                "emp_id": self.emp_id})
        return resp

    def __close_account(self, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"account_id": self.client_account_id,
                                                                                "emp_id": self.emp_id})
        return resp
