import requests
import os
import json
import pandas as pd


class CardRequestsMenu:
    def __init__(self, personal_token, emp_id):
        self.token = personal_token
        self.emp_id = emp_id
        self.url = "http://127.0.0.1:5000/v1/employee/cards"  # os.environ.get("BANK_URL") + "/v1/cards"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def __str__(self):
        return "------------------------------------- Card Requests -------------------------------------\n"

    def menu(self):
        df_requests = self.get_all_card_requests(self.url + "/card_requests")

        card_select = "X"
        while card_select not in [str(x) for x in range(1, df_requests.shape[0] + 1)]:
            for i in df_requests.index:
                print(f"[{i + 1}] Request date: {df_requests.at[i, 'request_date']} | "
                      f"Request: Brand = {df_requests.at[i, 'brand']}, Category = {df_requests.at[i, 'category']}, "
                      f"Type = {df_requests.at[i, 'type']}")
            card_select = input("Select one of the cards or type [B] to go back: ").lower()

            if card_select == "b":
                return False

        card_index = int(card_select) - 1

        decision = "X"
        while decision not in ["a", "d"]:
            print(f"Client balance: ${df_requests.at[card_index, 'balance']} | Total cards owned: "
                  f"{df_requests.at[card_index, 'total_cards_owned']} | Total statements paid late: "
                  f"{df_requests.at[card_index, 'total_late_paid_invoices']} | Request: Brand = "
                  f"{df_requests.at[card_index, 'brand']}, Category = {df_requests.at[card_index, 'category']}, "
                  f"Type = {df_requests.at[card_index, 'type']}")
            decision = input("Press [A] to approve this request, [D] to deny it or [B] to go back: ").lower()
            if decision == "b":
                return False

        approval = True if decision == "a" else False
        resp = self.__resolve_card_request(
            approval, df_requests.at[card_index, "request_id"], self.url + "/resolve_card_request"
        )
        if resp.status_code == 200:
            print("Request resolved successfully.")
            return False
        elif resp.status_code == 201:
            print("Card created successfully.")
            data = json.loads(resp.text)["data"]
            print(f"Activation Code: {data['activation_code']}. Card PIN: {data['card_pin']}")
            return False
        elif resp.status_code == 401:
            print("Token authentication failed.")
        else:
            print("There was an error. Please try again later.")

        return False


    def get_all_card_requests(self, request_url):
        resp = self.__get_card_requests(request_url)
        if resp.status_code == 200:
            df_card_requests = pd.DataFrame()
            for card_req_result in json.loads(resp.text)["data"]:
                req = dict()
                req["request_id"] = card_req_result["request_id"]
                req["request_date"] = card_req_result["request_date"]
                req["balance"] = card_req_result["balance"]
                req["brand"] = card_req_result["brand"]
                req["category"] = card_req_result["category"]
                req["type"] = card_req_result["type"]
                req["total_cards_owned"] = card_req_result["total_cards_owned"]
                req["total_late_paid_invoices"] = card_req_result["total_late_paid_invoices"]

                df_single_req = pd.DataFrame([list(req.values())], columns=list(req.keys()))
                df_card_requests = pd.concat([df_card_requests, df_single_req], ignore_index=True)

            return df_card_requests

        elif resp.status_code == 400:
            print("No card requests found.")
            return
        elif resp.status_code == 401:
            print("Token authentication failed.")
            return
        else:
            print("There was an error. Please try again later.")
            return


    def execute(self):
        no_exit = True
        while no_exit:
            print(self)
            no_exit = self.menu()

    def __get_card_requests(self, request_url):
        resp = requests.request("GET", request_url, headers=self.headers, data={"emp_id": self.emp_id})
        return resp

    def __resolve_card_request(self, approval, request_id, request_url):
        resp = requests.request("POST", request_url, headers=self.headers, data={"emp_id": self.emp_id,
                                                                                 "approval": approval,
                                                                                 "request_id": request_id})
        return resp
