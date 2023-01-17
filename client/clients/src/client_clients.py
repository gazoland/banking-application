import requests
import os

from client import resources

class ClientsMenu:
    def __init__(self, personal_token, client_id, pronoun, username, email, phone):
        self.token = personal_token
        self.client_id = client_id
        self.pronoun = pronoun
        self.username = username
        self.email = email
        self.phone = phone
        self.url = "http://127.0.0.1:5000/v1/clients"  # os.environ.get("BANK_URL") + "/v1/clients"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.endpoints = {
            "1": "/username",
            "2": "/password",
            "3": "/email",
            "4": "/phone",
            "5": "/pronoun"
        }

    def __str__(self):
        return "------------------- My Information -------------------\n"

    def menu(self):
        command = ""
        while command not in [str(x) for x in range(1, len(self.endpoints.keys()) + 1)] and command != "b":
            print("What would you like to do?\n"
                  "[1] Update Username\n"
                  "[2] Update Password\n"
                  "[3] Update Email\n"
                  "[4] Update Phone\n"
                  "[5] Update Treatment Pronoun\n"
                  "Or press [B] to go back to the main menu: ")
            command = input().lower()
        if command == "b":
            return False
        elif command == "1":
            self.update_username(self.url + self.endpoints[command])
        elif command == "2":
            self.update_password(self.url + self.endpoints[command])
        elif command == "3":
            self.update_email(self.url + self.endpoints[command])
        elif command == "4":
            self.update_phone(self.url + self.endpoints[command])
        elif command == "5":
            self.update_pronoun(self.url + self.endpoints[command])

        return True

    def update_username(self, request_url):
        while True:
            print(f"Your current username is: {self.username}")
            new_user = input("Type a new username or [B] to go back: ")

            if new_user in ["b", "B"]:
                return

            username_check = resources.new_username_check(new_user)
            if not username_check.valid:
                print(username_check.message)
                continue

            if new_user == self.username:
                print("New username must be different from current username.")
                continue

            resp = self.__post_value_to_update_request(new_user, self.username, request_url)
            if resp.status_code == 200:
                print("Username updated successfully.")
                self.username = new_user
                return
            elif resp.status_code == 409:
                print("Username is already taken. Please try another one.")
            elif resp.status_code == 401:
                print("Token authentication failed.")
            else:
                print("There was an error. Please try again later.")

    def update_password(self, request_url):
        # Implement email verification later?
        while True:
            print("Type [B] at anytime to go back.")
            old_pwd = input("Type your current password: ")
            if old_pwd in ["B", "b"]:
                return

            new_pwd = input("Type your new password: ")
            if new_pwd in ["B", "b"]:
                return

            new_pwd_check = resources.new_password_check(new_pwd)
            if not new_pwd_check.valid:
                print(new_pwd_check.message)
                continue

            confirm_new_pwd = input("Confirm your new password: ")
            if confirm_new_pwd in ["B", "b"]:
                return
            if new_pwd != confirm_new_pwd:
                print("New passwords are different from each other.")
                continue

            resp = self.__post_value_to_update_request(new_pwd, old_pwd, request_url)
            if resp.status_code == 200:
                print("Password updated successfully.")
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Current password doesn't match. Try again.")
            else:
                print(f"There was an error: {resp.status_code}: \n{resp.text} \nPlease try again later.")

    def update_email(self, request_url):
        # Implement email verification later?
        while True:
            print(f"Your current email is: {self.email}")
            new_email = input("Type your best email or [B] to go back: ")

            if new_email in ["b", "B"]:
                return

            new_email_check = resources.new_email_check(new_email)
            if not new_email_check.valid:
                print(new_email_check.message)
                continue

            if new_email == self.email:
                print("New email must be different from current email.")
                continue

            resp = self.__post_value_to_update_request(new_email, self.email, request_url)
            if resp.status_code == 200:
                print("Email updated successfully.")
                self.email = new_email
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Email is already taken. Please try another one.")
            else:
                print("There was an error. Please try again later.")

    def update_phone(self, request_url):
        # Implement phone verification later?
        while True:
            print(f"Your current phone is: {self.phone}")
            new_phone = input("Type your mobile number or [B] to go back: ")

            if new_phone in ["b", "B"]:
                return

            new_phone_check = resources.new_phone_check(new_phone)
            if not new_phone_check.valid:
                print(new_phone_check.message)
                continue

            if new_phone == self.phone:
                print("New phone must be different from current phone.")
                continue

            resp = self.__post_value_to_update_request(new_phone, self.phone, request_url)
            if resp.status_code == 200:
                print("Phone number updated successfully.")
                self.phone = new_phone
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("This phone number is already taken. Please try another one.")
            else:
                print("There was an error. Please try again later.")

    def update_pronoun(self, request_url):
        pronouns = {
            "1": "Mr.",
            "2": "Mrs.",
            "3": "Ms.",
            "4": "Miss",
            "5": "Mx.",
            "6": "Leave blank"
        }
        while True:
            for code, pronoun in pronouns.items():
                print(f"[{code}] {pronoun}")
            new_pronoun = input("Select a new treatment pronoun or [B] to go back: ")
            if new_pronoun in ["b", "B"]:
                return
            if new_pronoun not in pronouns.keys():
                print("Please select a valid option.")
                continue

            resp = self.__post_value_to_update_request(new_pronoun, self.pronoun, request_url)
            if resp.status_code == 200:
                print("Treatment pronoun updated successfully.")
                self.pronoun = pronouns[new_pronoun] if new_pronoun != "6" else ""
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            else:
                print("There was an error. Please try again later.")

    def execute(self):
        no_exit = True
        while no_exit:
            print(self)
            no_exit = self.menu()

    def __post_value_to_update_request(self, value, old_value, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"new_value": value,
                                                                                "old_value": old_value,
                                                                                "client_id": self.client_id})
        return resp
