from flask_restx import Resource, Namespace, reqparse, abort, inputs
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime

from src import resources


purchases_ns = Namespace("purchases", path="/purchases")

@purchases_ns.route("")
class Purchase(Resource):
    def post(self):
        purchase_args = PurchaseRequestArgs()

        card_args = self.__get_card_purchase_info(purchase_args.card_number)
        if purchase_args.pay_type == "debit":
            acc_args = self.__get_acc_purchase_info(purchase_args.card_number)
        else:
            acc_args = self.__get_statement_purchase_info(purchase_args.card_number)

        if card_args["active"] and card_args["unlocked"]:
            valid_purchase = self.__validate_purchase(purchase_args, card_args, acc_args)

            if valid_purchase:
                new_balance = None
                if purchase_args.pay_type == "debit":
                    new_balance = float(acc_args["balance"]) - purchase_args.purchase_total

                successful_purchase = resources.register_purchase(purchase_args, card_args, acc_args, new_balance)
                if successful_purchase:
                    return {"message": "Payment approved."}, 201

                abort(500, message="System error.")

        abort(400, message="Payment declined.")

    @staticmethod
    def __get_card_purchase_info(card_number:str) -> dict:
        values = resources.get_card_purchase_request_info(card_number)
        if not len(values):
            abort(400, message="Invalid Card.")
        purchase_card_info = dict()
        purchase_card_info["card_id"] = values[0][0]
        purchase_card_info["card_name"] = values[0][1]
        purchase_card_info["sec_code"] = values[0][2]
        purchase_card_info["pin"] = values[0][3]
        purchase_card_info["exp_date"] = values[0][4]
        purchase_card_info["card_type"] = values[0][5]
        purchase_card_info["active"] = values[0][6]
        purchase_card_info["unlocked"] = values[0][7]
        purchase_card_info["limit"] = values[0][8]

        return purchase_card_info

    @staticmethod
    def __get_acc_purchase_info(card_number:str) -> dict:
        values = resources.get_acc_purchase_request_info(card_number)
        if not len(values):
            abort(500, message="System error.")
        purchase_acc_info = dict()
        purchase_acc_info["account_id"] = values[0][0]
        purchase_acc_info["balance"] = values[0][1]

        return purchase_acc_info

    @ staticmethod
    def __get_statement_purchase_info(card_number:str) -> dict:
        values = resources.get_statement_purchase_request_info(card_number)
        if not len(values):
            abort(400, message="Invalid payment type.")
        purchase_statement_info = dict()
        purchase_statement_info["invoice_id"] = values[0][0]
        purchase_statement_info["invoice_total"] = values[0][1]

        return purchase_statement_info

    @staticmethod
    def __validate_purchase(purchase_args, card_args, acc_args):
        # Payment type
        if (purchase_args.pay_type not in ["credit", "debit"]) or \
        (purchase_args.pay_type == "credit" and card_args["card_type"] == "debit") or \
        (purchase_args.pay_type == "debit" and card_args["card_type"] == "credit"):
            abort(400, message="Invalid payment type.")

        # Card Information
        exp_date_split = purchase_args.card_exp_date.split("/")
        exp_date = date(year=int(exp_date_split[1]), month=int(exp_date_split[0]), day=1)

        card_fields = {
            "card_name": purchase_args.card_name == card_args["card_name"],
            "card_sec_code": purchase_args.card_sec_code == card_args["sec_code"],
            "exp_date": exp_date == card_args["exp_date"] and exp_date > datetime.now().date()
        }
        if not all(card_fields.values()):
            abort(400, message=f"Payment denied. Incorrect card information.")

        # Funds
        if purchase_args.pay_type == "debit" and purchase_args.purchase_total > acc_args["balance"]:
            abort(409, message="Payment declined.")
        if purchase_args.pay_type == "credit" and \
        purchase_args.purchase_total > (card_args["limit"] - acc_args["invoice_total"]):
            abort(409, message="Payment declined.")

        # PIN
        if not check_password_hash(card_args["pin"], purchase_args.card_pin):
            abort(401, message="Payment declined. Incorrect PIN.")

        return True


class PurchaseRequestArgs:
    def __init__(self):
        purchase_args = self.purchase_request_parser().parse_args()
        self.est_code = purchase_args["est_code"]
        self.est_location = purchase_args["est_location"]
        self.pay_type = purchase_args["pay_type"]
        self.purchase_total = purchase_args["purchase_total"]
        self.card_name = purchase_args["card_name"]
        self.card_number = purchase_args["card_number"]
        self.card_exp_date = purchase_args["card_exp_date"]
        self.card_sec_code = purchase_args["card_sec_code"]
        self.card_pin = purchase_args["card_pin"]

    @staticmethod
    def purchase_request_parser():
        purchase_parser = reqparse.RequestParser()
        purchase_parser.add_argument(
            "est_code", type=str, help="Establishment code is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "est_location", type=str, help="Establishment location is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "pay_type", type=str, help="Payment type is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "purchase_total", type=float, help="Purchase total is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "card_name", type=str, help="Card name is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "card_number", type=str, help="Card number is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "card_exp_date", type=str, help="Card expiration date is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "card_sec_code", type=int, help="Card security code is missing.", location="form", required=True
        )
        purchase_parser.add_argument(
            "card_pin", type=str, help="Card PIN is missing.", location="form", required=True
        )

        return purchase_parser
