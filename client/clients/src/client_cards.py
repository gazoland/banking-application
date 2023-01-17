import requests
import os
import json
import pandas as pd

class CardsMenu:
    def __init__(self, personal_token, account_id, balance):
        self.token = personal_token
        self.account_id = account_id
        self.balance = balance
        self.url = "http://127.0.0.1:5000/v1/cards"  # os.environ.get("BANK_URL") + "/v1/cards"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.endpoints = {
            "1": "/my_cards",
            "2": "/pay_statements",
            "3": "/activate",
            "4": "/request"
        }

    def __str__(self):
        return "------------------- Cards Menu -------------------\n"

    def menu(self):
        command = ""
        while command not in [str(x) for x in range(1, len(self.endpoints.keys()) + 1)] and command != "b":
            print("What would you like to do?\n"
                  "[1] My Cards\n"
                  "[2] Pay A Card Statement With Account Balance\n" 
                  "[3] Activate Card\n"
                  "[4] Get New Card\n"
                  "Or press [B] to go back to the main menu: ")
            command = input().lower()
        if command == "b":
            return False
        elif command == "1":
            self.my_cards(self.url + self.endpoints[command])
        elif command == "2":
            self.pay_statements(self.url + self.endpoints[command])
        elif command == "3":
            self.activate_card(self.url + self.endpoints[command])
        elif command == "4":
            self.ask_for_new_card(self.url + self.endpoints[command])

        return True

    def my_cards(self, request_url):
        resp = self.__get_all_cards_request(request_url)
        if resp.status_code == 200:
            df_cards = pd.DataFrame()
            for card_result in json.loads(resp.text)["data"]["cards_list"]:
                card_info = dict()
                card_info["id"] = card_result["card_id"]
                card_info["number"] = card_result["number"]
                card_info["type"] = card_result["type"]
                card_info["brand"] = card_result["brand"]
                card_info["category"] = card_result["category"]
                card_info["unlocked"] = card_result["unlocked"]
                card_info["statement_day"] = card_result["statement_day"]
                card_info["current_limit"] = card_result["current_limit"]

                df_single_card = pd.DataFrame([list(card_info.values())], columns=list(card_info.keys()))
                df_cards = pd.concat([df_cards, df_single_card], ignore_index=True)

        elif resp.status_code == 400:
            print("No cards found.")
            return
        elif resp.status_code == 401:
            print("Token authentication failed.")
            return
        else:
            print("There was an error. Please try again later.")
            return

        card_select = "X"
        while card_select not in [str(x) for x in range(1, df_cards.shape[0] + 1)]:
            print("--------------------------------- My Cards ---------------------------------")
            for i in df_cards.index:
                print(f"[{i+1}] {df_cards.at[i, 'number']} | {df_cards.at[i, 'brand']} - "
                      f"{df_cards.at[i, 'category']} - {df_cards.at[i, 'type']} | "
                      f"{'Unl' if df_cards.at[i, 'unlocked'] else 'L'}ocked")
            card_select = input("Select one of the cards or type [B] to go back: ").lower()
            if card_select == "b":
                return

        MyCard(
            personal_token=self.token,
            url=request_url,
            account=self.account_id,
            card_id=df_cards.at[int(card_select) - 1, "id"],
            card_number=df_cards.at[int(card_select) - 1, "number"],
            brand=df_cards.at[int(card_select) - 1, "brand"],
            category=df_cards.at[int(card_select) - 1, "category"],
            card_type=df_cards.at[int(card_select) - 1, "type"],
            unlocked=df_cards.at[int(card_select) - 1, "unlocked"],
            statement_day=df_cards.at[int(card_select) - 1, "statement_day"],
            current_limit=df_cards.at[int(card_select) - 1, "current_limit"]
        ).execute()

    def pay_statements(self, request_url):
        resp = self.__get_all_payable_statements_request(request_url)
        if resp.status_code == 200:
            self.statements_menu(json.loads(resp.text)["data"]["statements"],  request_url)
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")
        return


    def statements_menu(self, data, request_url):
        statement_select = "X"
        while statement_select not in [str(x) for x in range(1, len(data) + 1)]:
            print(f"Current balance: ${self.balance}")
            for i in range(len(data)):
                print(f"[{i + 1}] {data[i]['dt_start']} | {data[i]['dt_end']} - Due date: {data[i]['dt_due']} - "
                      f"Status: {data[i]['status']} - Total: ${data[i]['total']}")
            statement_select = input(
                "Select statement you would like to pay with your balance or press [B] to go back: "
            ).lower()
            if statement_select == "b":
                return
        st_index = int(statement_select) - 1

        confirm_pay = 'X'
        while confirm_pay not in ("b", "y"):
            confirm_pay = input(f"Paying statement from {data[st_index]['dt_start']} to {data[st_index]['dt_end']} "
                                f"with your account balance. Total = ${data[st_index]['total']}\n"
                                f"Press [Y] to confirm or [B] to go back: ").lower()

            if confirm_pay == "b":
                break

            elif confirm_pay == "y":
                st_id = data[st_index]["id"]
                st_card_id = data[st_index]["card_id"]
                resp = self.__pay_statement_request(st_id, st_card_id, request_url + "/pay")
                if resp.status_code == 200:
                    print("Payment confirmed. Thank you!")
                    self.balance -= data[st_index]['total']
                    return
                elif resp.status_code == 401:
                    print("Token authentication failed.")
                else:
                    print("There was an error. Please try again later.")
                return

    def activate_card(self, request_url):
        while True:
            code = input("Type your card activation code or [B] to go back: ").lower()
            if code == "b":
                return
            if not code.isdigit() or len(code) != 6:
                print('Invalid code. Please try again.')
                continue

            resp = self.__activate_card_request(request_url, code)
            if resp.status_code == 200:
                print("Activation successful! You can now use your card.")
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Invalid activation code. Try again.")
            else:
                print("There was an error. Please try again later.")

    def ask_for_new_card(self, request_url):
        card_brands = {
            "1": "MasterCard",
            "2": "Visa",
            "3": "American Express"
        }
        card_categories = {
            "1": "Silver",
            "2": "Gold",
            "3": "Platinum",
            "4": "Black"
        }
        card_types = {
            "1": "Debit",
            "2": "Credit",
            "3": "Debit/Credit"
        }
        card_brand = "X"
        while card_brand not in card_brands.keys():
            for brand_id, brand_name in card_brands.items():
                print(f"[{brand_id}] {brand_name}")
            card_brand = input("Type the card brand or [B] to go back: ").lower()
            if card_brand == "b":
                return
        card_category = "X"
        while card_category not in card_categories.keys():
            for category_id, category_name in card_categories.items():
                print(f"[{category_id}] {category_name}")
            card_category = input("Type the card category or [B] to go back: ").lower()
            if card_category == "b":
                return
        card_type = "X"
        while card_type not in card_types.keys():
            for type_id, type_name in card_types.items():
                print(f"[{type_id}] {type_name}")
            card_type = input("Type the card brand or [B] to go back: ").lower()
            if card_type == "b":
                return
        resp = self.__ask_for_new_card_request(request_url, card_brand, card_category, card_types[card_type].lower())
        if resp.status_code == 201:
            print("Your request for a new card was made. You will soon get a reply from us. Thank you!")
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

    def __activate_card_request(self, request_url, code):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"activation_code": code,
                                                                                "account_id": self.account_id})
        return resp

    def __ask_for_new_card_request(self, request_url, brand_id, category_id, card_type):
        resp = requests.request("POST", request_url, headers=self.headers, data={"brand_id": brand_id,
                                                                                 "category_id": category_id,
                                                                                 "card_type": card_type,
                                                                                 "account_id": self.account_id
                                                                                 })
        return resp

    def __get_all_payable_statements_request(self, request_url):
        resp = requests.request("GET", request_url, headers=self.headers, data={"account_id": self.account_id})
        return resp

    def __pay_statement_request(self, statement_id, card_id, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"account_id": self.account_id,
                                                                                "card_id": card_id,
                                                                                "statement_id": statement_id})
        return resp

    def __get_all_cards_request(self, request_url):
        resp = requests.request("GET", request_url, headers=self.headers, data={"account_id": self.account_id})
        return resp


class MyCard:
    def __init__(
            self,
            personal_token,
            url,
            account,
            card_id,
            card_number,
            brand,
            category,
            card_type,
            unlocked,
            statement_day,
            current_limit
        ):
        self.token = personal_token
        self.url = url
        self.account_id = account
        self.card_id = card_id
        self.number = card_number
        self.brand = brand
        self.category = category
        self.type = card_type
        self.unlocked = unlocked
        self.statement_day = statement_day
        self.current_limit = current_limit
        self.headers = {"Accept": "application/json",
                        "Authorization": f"Bearer {self.token}"}
        self.endpoints = {
            "1": "/lock",
            "2": "/change_pin",
            "3": "/card_statements",
            "4": "/change_statement_day",
            "5": "/change_limit"
        }

    def __str__(self):
        return f"{self.number} | {self.brand} - {self.category} - {self.type} | {'Unl' if self.unlocked else 'L'}ocked"

    def menu(self):
        lock_string = "Unl" if not self.unlocked else "L"
        command = ""
        while command not in [str(x) for x in range(1, len(self.endpoints.keys()) + 1)] and command != "b":
            print("What would you like to do?\n"
                  f"[1] {lock_string}ock card\n"
                  "[2] Change PIN")
            if self.type != "debit":
                print("[3] Get Card Statements\n"
                      "[4] Change Statement Day\n"
                      "[5] Change Card Limit")
            command = input("Or press [B] to go back to the cards menu: ").lower()
            if self.type == "debit" and command in ("3", "4", "5"):
                command = "x"

        if command == "b":
            return False
        elif command == "1":
            self.lock_unlock(self.url + self.endpoints[command], lock_string)
        elif command == "2":
            self.change_pin(self.url + self.endpoints[command])
        elif command == "3":
            self.get_card_statements(self.url + self.endpoints[command])
        elif command == "4":
            self.change_statement_day(self.url + self.endpoints[command])
        elif command == "5":
            self.change_current_limit(self.url + self.endpoints[command])

        return True

    def lock_unlock(self, request_url, lock_string):
        confirm = "X"
        while confirm not in ("b", "y"):
            confirm = input(f"{lock_string}ock card? Press [Y] to confirm or [B] to go back: ").lower()
        if confirm == "y":
            resp = self.__lock_unlock_request(request_url)
            if resp.status_code == 200:
                print(f"Card {lock_string}ocked.")
                self.unlocked = not self.unlocked
                return
            elif resp.status_code == 401:
                print("Token authentication failed.")
            else:
                print("There was an error. Please try again later.")

    def get_card_statements(self, request_url):
        resp = self.__all_card_statements_request(request_url)
        if resp.status_code == 200:
            self.statements_menu(json.loads(resp.text)["data"]["statements"])
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")
        return

    def statements_menu(self, data):
        statement_select = "X"
        while statement_select not in [str(x) for x in range(1, len(data) + 1)]:
            for i in range(len(data)):
                print(f"[{i + 1}] {data[i]['dt_start']} | {data[i]['dt_end']} - "
                      f"{data[i]['status']} - Total: ${data[i]['total']}")
            statement_select = input("Select statement or press [B] to go back: ").lower()
            if statement_select == "b":
                return

        st_id = data[int(statement_select) - 1]["id"]
        resp = self.__get_card_statement_request(st_id, self.url + "/statement")
        if resp.status_code == 200:
            for transaction in json.loads(resp.text)["data"]["transactions"]:
                print(transaction)
            return
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")
        return

    def change_pin(self, request_url):
        while True:
            old_pin = input("Type your current PIN or [B] to go back: ").lower()
            if old_pin == "b":
                return
            if not old_pin.isdigit() or len(old_pin) != 4:
                print("Invalid PIN. Please type your 4-digit PIN again.")
                continue

            new_pin = input("Type your new PIN or [B] to go back: ").lower()
            if new_pin == "b":
                return
            if not new_pin.isdigit() or len(new_pin) != 4:
                print("Invalid PIN. Please type your new 4-digit PIN again.")
                continue

            resp = self.__change_value_request(request_url, old_pin, new_pin)
            if resp.status_code == 200:
                print("PIN updated successfully.")
                return
            elif resp.status_code == 400:
                print("Card PIN error.")
            elif resp.status_code == 401:
                print("Token authentication failed.")
            elif resp.status_code == 409:
                print("Old PIN doesn't match. Try again.")
            else:
                print("There was an error. Please try again later.")

    def change_statement_day(self, request_url):
        while True:
            print(f"Your card's statement day is: {self.statement_day}.")
            print("Please select a new statement day for your card:\n"
                  "05\n"
                  "10\n"
                  "15\n"
                  "20\n"
                  "25\n"
                  "Or press [B] to go back to the cards menu: ")
            new_day = input().lower()
            if new_day == "b":
                return
            elif new_day in ("5", "05", "10", "15", "20", "25"):
                new_day = "05" if new_day == "5" else new_day

                resp = self.__change_value_request(request_url, self.statement_day, new_day)
                if resp.status_code == 200:
                    print("Card's statement day updated successfully.")
                    self.statement_day = new_day
                    return
                elif resp.status_code == 400:
                    print("Invalid statement day.")
                elif resp.status_code == 401:
                    print("Token authentication failed.")
                else:
                    print("There was an error. Please try again later.")

    def change_current_limit(self, request_url):
        while True:
            print(f"Your card limit is: {self.current_limit}.")
            new_limit = input("Please enter a new limit between $200 and $5,000. Or [B] to go back: ").lower()
            if new_limit == "b":
                return
            elif not new_limit.isdigit() or int(new_limit) < 200 or int(new_limit) > 5000:
                print("Please type only digits inside the accepted interval.")
                continue
            resp = self.__change_value_request(request_url, self.current_limit, new_limit)
            if resp.status_code == 200:
                print("Card limit updated successfully.")
                return
            elif resp.status_code == 400:
                print("Invalid limit.")
            elif resp.status_code == 401:
                print("Token authentication failed.")
            else:
                print("There was an error. Please try again later.")


    def execute(self):
        no_exit = True
        while no_exit:
            print(self)
            no_exit = self.menu()

    def __lock_unlock_request(self, request_url):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"account_id": self.account_id,
                                                                                "card_id": self.card_id})
        return resp

    def __all_card_statements_request(self, request_url):
        resp = requests.request("GET", request_url, headers=self.headers, data={"account_id": self.account_id,
                                                                                "card_id": self.card_id})
        return resp

    def __get_card_statement_request(self, st_id, request_url):
        resp = requests.request("GET", request_url, headers=self.headers, data={"account_id": self.account_id,
                                                                                "card_id": self.card_id,
                                                                                "statement_id": st_id
                                                                                })
        return resp

    def __change_value_request(self, request_url, old_value, new_value):
        resp = requests.request("PUT", request_url, headers=self.headers, data={"old_value": old_value,
                                                                                "new_value": new_value,
                                                                                "account_id": self.account_id,
                                                                                "card_id": self.card_id})
        return resp
