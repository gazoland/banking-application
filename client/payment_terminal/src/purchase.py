import json
import requests

from client import resources


class PurchaseMenu:
    def __init__(self, est_code, location):
        self.url = "http://127.0.0.1:5000/v1/purchases"  # Would come from the card info, according to its bank
        self.est_code = est_code
        self.location = location
        self.pay_type = None
        self.purchase_total = None
        self.card_name = None
        self.card_number = None
        self.card_exp_date = None
        self.card_sec_code = None
        self.card_pin = None

    def menu(self):
        pay_type = self.__get_payment_type()
        if not pay_type:
            return

        total = self.__get_purchase_total()
        if not total:
            return

        card_info = self.__get_card_info()
        if not card_info:
            return

        resp = self.__make_purchase_request(self.url)
        print(json.loads(resp.text)["message"])
        return

    def __get_payment_type(self) -> bool:
        pay_type_ref = {"1": "debit", "2": "credit"}
        pay_type = ""
        while pay_type not in ["1", "2"] and pay_type != "b":
            print("Please select the type of payment: \n"
                  "[1] Debit\n"
                  "[2] Credit\n"
                  "Or Press [B] to go back: ")
            pay_type = input().lower()

        if pay_type == "b":
            return False

        self.pay_type = pay_type_ref[pay_type]
        return True

    def __get_purchase_total(self) -> bool:
        while True:
            purchase_total = input("Type in the purchase total [B] to go back: ")
            if purchase_total in ["b", "B"]:
                return False

            total_check = resources.valid_amount_check(purchase_total)
            if not total_check.valid:
                print(total_check.message)
                continue
            break

        self.purchase_total = float(purchase_total)
        return True

    def __get_card_info(self) -> bool:
        card_name = input("Type in the name on the card or [B] to go back: ").upper()
        if card_name == "B":
            return False

        while True:
            card_number = input("Type in the card number or [B] to go back: ").lower()
            if card_number == "b":
                return False

            card_number_check = resources.valid_card_number_check(card_number)
            if not card_number_check.valid:
                print(card_number_check.message)
                continue
            break

        while True:
            card_sec_code = input("Type in the card security code or [B] to go back: ").lower()
            if card_sec_code == "b":
                return False

            card_sec_code_check = resources.valid_card_sec_code_check(card_sec_code)
            if not card_sec_code_check.valid:
                print(card_sec_code_check.message)
                continue
            break

        while True:
            card_exp_date = input("Type in the card expiration date or [B] to go back: ").lower()
            if card_exp_date == "b":
                return False

            card_exp_date_check = resources.valid_card_exp_date_check(card_exp_date)
            if not card_exp_date_check.valid:
                print(card_exp_date_check.message)
                continue
            break

        while True:
            card_pin = input("Type in the card PIN or [B] to go back: ").lower()
            if card_pin == "b":
                return False

            card_pin_check = resources.valid_card_pin_check(card_pin)
            if not card_pin_check.valid:
                print(card_pin_check.valid)
                continue
            break

        self.card_name = card_name
        self.card_number = card_number
        self.card_sec_code = int(card_sec_code)
        self.card_exp_date = card_exp_date
        self.card_pin = card_pin
        return True

    def __make_purchase_request(self, request_url):
        resp = requests.request("POST", url=request_url, data={"est_code": self.est_code,
                                                               "est_location": self.location,
                                                               "pay_type": self.pay_type,
                                                               "purchase_total": self.purchase_total,
                                                               "card_name": self.card_name,
                                                               "card_number": self.card_number,
                                                               "card_exp_date": self.card_exp_date,
                                                               "card_sec_code": self.card_sec_code,
                                                               "card_pin": self.card_pin})
        return resp
