from flask_restx import Resource, Namespace, reqparse, abort, inputs
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash

from src import resources


cards_ns = Namespace("cards", path="/cards")
my_cards_ns = Namespace("my_cards", path="/cards/my_cards")
emp_cards_ns = Namespace("card_requests", path="/employee/cards")


@cards_ns.route("/my_cards")
class CardListCards(Resource):
    @resources.token_required
    def get(self):
        get_card_args = CardArgs("list_cards")
        return self.__get_card_list(get_card_args.account_id)

    @staticmethod
    @resources.user_authorization
    def __get_card_list(account_id):
        resp = resources.get_card_list(account_id)
        if len(resp):
            cards = list()
            for row in resp:
                card_data = dict()
                card_data["card_id"] = row[0]
                card_data["number"] = "*"*12 + row[1][12:]
                card_data["type"] = row[2]
                card_data["brand"] = row[3]
                card_data["category"] = row[4]
                card_data["unlocked"] = row[5]
                card_data["statement_day"] = row[6]
                card_data["current_limit"] = row[7]

                cards.append(card_data)

            return {"response": "Success", "data": {"cards_list": cards}}

        abort(400, "No cards found.")


@cards_ns.route("/pay_statements")
class CardPayableStatements(Resource):
    @resources.token_required
    def get(self):
        get_card_args = CardArgs("list_statements")
        return self.__get_statements_list(get_card_args.account_id)

    @staticmethod
    @resources.user_authorization
    def __get_statements_list(account_id):
        st_res = resources.get_payable_statements_list(account_id)
        statements = list()
        for statement_row in range(len(st_res)):
            statement = dict()
            statement["dt_start"] = st_res[statement_row][0].strftime("%Y-%m-%d")
            statement["dt_end"] = st_res[statement_row][1].strftime("%Y-%m-%d")
            statement["dt_due"] = st_res[statement_row][2].strftime("%Y-%m-%d")
            statement["status"] = st_res[statement_row][3]
            statement["total"] = float(st_res[statement_row][4])
            statement["id"] = st_res[statement_row][5]
            statement["card_id"] = st_res[statement_row][6]

            statements.append(statement)

        resp_dict = {"response": "Success", "data": {"statements": statements}}
        return resp_dict, 200


@cards_ns.route("/pay_statements/pay")
class CardPayStatement(Resource):
    @resources.token_required
    def put(self):
        get_card_args = CardArgs("pay_statement")
        return self.__pay_card_statement(get_card_args.account_id, get_card_args.card_id, get_card_args.statement_id)

    @staticmethod
    @resources.user_authorization
    def __pay_card_statement(account_id, card_id, statement_id):
        acc_data = resources.get_account_info(account_id)
        statement_total = resources.get_paying_statement_info(card_id, statement_id)
        if len(statement_total):
            total = statement_total[0][0]
            if len(acc_data):
                balance = acc_data[0][0]
                if balance > total:
                    new_balance = balance - total
                    successful_payment = resources.pay_card_statement(account_id, card_id, statement_id, new_balance, total)
                    if successful_payment:
                        return make_response("Success.", 200)
                    abort(500, message="Database error.")
                abort(400, message="Insufficient funds.")
            abort(400, message="Error with account information.")
        abort(400, message="Statement not found.")


@cards_ns.route("/activate")
class CardActivate(Resource):
    @resources.token_required
    def put(self):
        card_args = CardArgs("activation")
        return self.__activate_card(card_args.account_id, card_args.activation_code)

    @staticmethod
    @resources.user_authorization
    def __activate_card(account_id, activation_code):
        check_deactivated_card = resources.get_deactivated_card(account_id)
        if len(check_deactivated_card):
            codes = dict()
            for row in check_deactivated_card:
                codes[row[1]] = row[0]  # {activation_code: card_id}
            if activation_code in codes.keys():
                activation_sucess = resources.activate_card(activation_code, codes[activation_code])
                if activation_sucess:
                    return make_response("Success.", 200)

                abort(500, message="Database error.")

            abort(409, message="Activation code not valid.")

        abort(400, message="No card to activate.")


@cards_ns.route("/request")
class CardRequest(Resource):
    @resources.token_required
    def post(self):
        card_request_args = CardArgs("card_request")
        return self.__make_card_request(
            card_request_args.account_id,
            card_request_args.brand_id,
            card_request_args.category_id,
            card_request_args.card_type
        )

    @staticmethod
    @resources.user_authorization
    def __make_card_request(account_id, brand_id, category_id, card_type):
        request_success = resources.make_card_request(account_id, brand_id, category_id, card_type)
        if request_success:
            return make_response("The card request was made successfully.", 201)
        abort(500, message="Database error.")


@my_cards_ns.route("/lock")
class MyCardLock(Resource):
    @resources.token_required
    def put(self):
        mycard_args = MyCardArgs("unlock")
        return self.__change_card_lock(mycard_args.account_id, mycard_args.card_id)

    @staticmethod
    @resources.user_authorization
    def __change_card_lock(account_id, card_id):
        lock_change_success = resources.change_card_lock(account_id, card_id)
        if lock_change_success:
            return make_response("Success", 200)
        abort(500, "Database error.")


@my_cards_ns.route("/card_statements")
class MyCardAllStatements(Resource):
    @resources.token_required
    def get(self):
        mycard_args = MyCardArgs("all_statements")
        return self.__get_card_statements(mycard_args.card_id, mycard_args.account_id)

    @staticmethod
    @resources.user_authorization
    def __get_card_statements(card_id, account_id):
        st_res = resources.get_all_card_statements(card_id, account_id)
        statements = list()
        for statement_row in range(len(st_res)):
            statement = dict()
            statement["dt_start"] = st_res[statement_row][0].strftime("%Y-%m-%d")
            statement["dt_end"] = st_res[statement_row][1].strftime("%Y-%m-%d")
            statement["status"] = st_res[statement_row][2]
            statement["total"] = float(st_res[statement_row][3])
            statement["id"] = st_res[statement_row][4]

            statements.append(statement)

        resp_dict = {"response": "Success", "data": {"statements": statements}}
        return resp_dict, 200


@my_cards_ns.route("/statement")
class MyCardStatement(Resource):
    @resources.token_required
    def get(self):
        mycard_args = MyCardArgs("statement")
        return self.__get_card_statement(mycard_args.account_id, mycard_args.card_id, mycard_args.statement_id)

    @staticmethod
    @resources.user_authorization
    def __get_card_statement(account_id, card_id, statement_id):
        st_res = resources.get_card_statement(account_id, card_id, statement_id)
        transactions = list()
        for transaction_row in range(len(st_res)):
            transaction = dict()
            transaction["amount"] = float(st_res[transaction_row][0])
            transaction["establishment"] = st_res[transaction_row][1]
            transaction["location"] = st_res[transaction_row][2]
            transaction["status"] = st_res[transaction_row][3]
            transaction["transaction_date"] = st_res[transaction_row][4].strftime("%Y-%m-%d %H:%M:%S.%f")

            transactions.append(transaction)

        resp_dict = {"response": "Success", "data": {"transactions": transactions}}
        return resp_dict, 200


@my_cards_ns.route("/change_pin")
class MyCardChangePIN(Resource):
    @resources.token_required
    def put(self):
        mycard_args = MyCardArgs("change_pin")
        return self.__change_card_pin(mycard_args.account_id,
                                      mycard_args.card_id,
                                      mycard_args.old_value,
                                      mycard_args.new_value)

    @staticmethod
    @resources.user_authorization
    def __change_card_pin(account_id, card_id, old_pin, new_pin):
        if not new_pin.isdigit() or len(new_pin) != 4:
            abort(400, message="New PIN is not valid.")
        stored_pin = resources.get_card_pin(account_id, card_id)
        if stored_pin:
            if check_password_hash(stored_pin[0][0], old_pin):
                new_pin_hash = generate_password_hash(new_pin)
                successful_update = resources.update_card_pin(account_id, card_id, new_pin_hash)
                if successful_update:
                    return make_response("Success.", 200)
                abort(500, message="Database error.")

            abort(409, message="Current PIN is incorrect.")

        abort(400, message="Card not found.")


@my_cards_ns.route("/change_statement_day")
class MyCardChangeStatementDay(Resource):
    @resources.token_required
    def put(self):
        mycard_args = MyCardArgs("change_pin")
        return self.__change_card_statement_day(mycard_args.account_id, mycard_args.card_id, mycard_args.new_value)

    @staticmethod
    @resources.user_authorization
    def __change_card_statement_day(account_id, card_id, new_day):
        if new_day not in ("05", "10", "15", "20", "25"):
            abort(400, "Statement day not valid.")
        successful_update = resources.update_card_statement_day(account_id, card_id, new_day)
        if successful_update:
            return make_response("Success.", 200)
        abort(500, message="Database error.")


@my_cards_ns.route("/change_limit")
class MyCardChangeLimit(Resource):
    @resources.token_required
    def put(self):
        mycard_args = MyCardArgs("change_limit")
        return self.__change_card_limit(mycard_args.account_id, mycard_args.card_id, int(mycard_args.new_value))

    @staticmethod
    @resources.user_authorization
    def __change_card_limit(account_id, card_id, new_limit):
        if new_limit < 200 or new_limit > 5000:
            abort(400, message="Invalid limit input.")
        successful_update = resources.update_card_limit(account_id, card_id, new_limit)
        if successful_update:
            return make_response("Success.", 200)
        abort(500, message="Database error.")


@emp_cards_ns.route("/new_client_card")
class EmployeeCreateNewClientCard(Resource):
    @resources.token_required
    def post(self):
        card_args = NewClientCreateCardArgs()
        return self.__create_card(
            card_args.account_id,
            card_args.brand_id,
            card_args.category_id,
            card_args.card_type,
            card_args.pin
        )

    @staticmethod
    @resources.admin_authorization
    def __create_card(account_id, brand_id, category_id, card_type, pin):
        client_name = resources.get_client_name_with_account_id(account_id)[0][0]
        new_card_args = resources.generate_card_args(client_name, pin, card_type, category_id)
        successful_card = resources.create_new_card(
            account_id,
            new_card_args["card_number"],
            new_card_args["card_name"],
            new_card_args["sec_code"],
            generate_password_hash(str(new_card_args["pin"])),
            new_card_args["exp_date"],
            new_card_args["activation_code"],
            card_type,
            brand_id,
            category_id,
            limit=None
        )
        if successful_card:
            resp = {"response": "Success", "data": {"activation_code": new_card_args["activation_code"]}}
            return make_response(resp, 200)
        abort(500, message="Database error.")


@emp_cards_ns.route("/resolve_card_request")
class EmployeeResolveCardRequest(Resource):
    @resources.token_required
    def post(self):
        card_args = ResolveCardRequestArgs()
        return self.__resolve_card_request(card_args.request_id, card_args.approval, card_args.emp_id)

    @staticmethod
    @resources.admin_authorization
    def __resolve_card_request(request_id, approval, emp_id):
        emp_name = resources.get_employee_name_with_id(emp_id)[0][0]
        if not approval:
            successful_denial = resources.deny_card_request(request_id, emp_name)
            if successful_denial:
                return make_response("Success.", 200)
            abort(500, message="Database update error.")

        card_info_res = resources.get_new_card_request_info(request_id)[0]
        card_info = dict()
        card_info["brand_id"] = card_info_res[0]
        card_info["category_id"] = card_info_res[1]
        card_info["type"] = card_info_res[2]
        card_info["account_id"] = card_info_res[3]
        card_info["full_name"] = card_info_res[4]

        new_card_args = resources.generate_card_args(
            card_info["full_name"], None, card_info["type"], card_info["category_id"]
        )
        hash_pin = generate_password_hash(new_card_args["pin"])
        successful_card_approval = resources.approve_card_request(
            account_id=card_info["account_id"],
            card_number=new_card_args["card_number"],
            card_name=new_card_args["card_name"],
            sec_code=new_card_args["sec_code"],
            pin=hash_pin,
            exp_date=new_card_args["exp_date"],
            activation_code=new_card_args["activation_code"],
            card_type=card_info["type"],
            brand_id=card_info["brand_id"],
            category_id=card_info["category_id"],
            limit=new_card_args["limit"],
            emp_name=emp_name,
            statement_day='05',
            request_id=request_id
        )

        if successful_card_approval:
            resp = {"response": "Success", "data": {"activation_code": new_card_args["activation_code"],
                                                    "card_pin": new_card_args["pin"]}}
            return make_response(resp, 201)
        abort(500, message="Database error.")



@emp_cards_ns.route("/card_requests")
class CardRequestsList(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        reqs = resources.get_card_requests()
        all_requests = list()
        for row in reqs:
            req = dict()
            req["request_id"] = row[0]
            req["request_date"] = row[1].strftime("%Y-%m-%d")
            req["balance"] = row[2]
            req["brand"] = row[3]
            req["category"] = row[4]
            req["type"] = row[5]
            req["total_cards_owned"] = row[6]
            req["total_late_paid_invoices"] = 0 if row[7] is None else row[7]
            all_requests.append(req)

        return make_response({"response": "Success", "data": all_requests}, 200)


class CardArgs:
    def __init__(self, request_type):
        card_args = self.create_card_parser(request_type).parse_args()
        self.account_id = card_args["account_id"]
        if request_type == "activation":
            self.activation_code = card_args["activation_code"]
        elif request_type == "card_request":
            self.brand_id = card_args["brand_id"]
            self.category_id = card_args["category_id"]
            self.card_type = card_args["card_type"]
        elif request_type == "pay_statement":
            self.card_id = card_args["card_id"]
            self.statement_id = card_args["statement_id"]


    @staticmethod
    def create_card_parser(request_type):
        card_parser = reqparse.RequestParser()
        if request_type == "activation":
            card_parser.add_argument(
                "activation_code", type=str, help="Activation code is required.", location="form", required=True
            )
        elif request_type == "card_request":
            card_parser.add_argument(
                "brand_id", type=int, help="Card brand ID is missing.", location="form", required=True
            )
            card_parser.add_argument(
                "category_id", type=int, help="Card category ID is missing.", location="form", required=True
            )
            card_parser.add_argument(
                "card_type", type=str, help="Card type ID is missing.", location="form", required=True
            )
        elif request_type == "pay_statement":
            card_parser.add_argument(
                "card_id", type=int, help="Card ID is missing.", location="form", required=True
            )
            card_parser.add_argument(
                "statement_id", type=int, help="Statement ID is missing.", location="form", required=True
            )
        elif request_type not in  ("list_cards", "list_statements"):
            raise KeyError("Invalid request type.")
        card_parser.add_argument(
            "account_id", type=int, help="ID of account is required.", location="form", required=True
        )
        return card_parser


class MyCardArgs:
    def __init__(self, request_type):
        mycard_args = self.create_mycard_parser(request_type).parse_args()
        self.account_id = mycard_args["account_id"]
        self.card_id = mycard_args["card_id"]
        if request_type == "statement":
            self.statement_id = mycard_args["statement_id"]
        if request_type in ("change_pin", "change_statement_day", "change_limit"):
            self.new_value = mycard_args["new_value"]
            self.old_value = mycard_args["old_value"] if request_type == "change_pin" else None

    @staticmethod
    def create_mycard_parser(request_type):
        mycard_parser = reqparse.RequestParser()
        if request_type in ("change_pin", "change_statement_day", "change_limit"):
            mycard_parser.add_argument(
                "new_value", type=str, help="New value is required.", location="form", required=True
            )
            if request_type == "change_pin":
                mycard_parser.add_argument(
                    "old_value", type=str, help="Old PIN is required.", location="form", required=True
                )
        elif request_type == "statement":
            mycard_parser.add_argument(
                "statement_id", type=str, help="Statement ID is required.", location="form", required=True
            )
        elif request_type not in  ("unlock", "all_statements"):
            raise KeyError("Invalid request type.")
        mycard_parser.add_argument(
            "account_id", type=int, help="ID of account is required.", location="form", required=True
        )
        mycard_parser.add_argument(
            "card_id", type=int, help="ID of card is required.", location="form", required=True
        )
        return mycard_parser


class NewClientCreateCardArgs:
    def __init__(self):
        card_args = self.create_card_parser().parse_args()
        self.account_id = card_args["account_id"]
        self.brand_id = card_args["brand_id"]
        self.category_id = card_args["category_id"]
        self.card_type = card_args["card_type"]
        self.pin = card_args["pin"]

    @staticmethod
    def create_card_parser():
        card_parser = reqparse.RequestParser()
        card_parser.add_argument(
            "brand_id", type=int, help="Card brand ID is missing.", location="form", required=True
        )
        card_parser.add_argument(
            "category_id", type=int, help="Card category ID is missing.", location="form", required=True
        )
        card_parser.add_argument(
            "card_type", type=str, help="Card type ID is missing.", location="form", required=True
        )
        card_parser.add_argument(
            "account_id", type=int, help="ID of account is missing.", location="form", required=True
        )
        card_parser.add_argument(
            "pin", type=int, help="Card PIN is missing.", location="form", required=True
        )
        return card_parser


class ResolveCardRequestArgs:
    def __init__(self):
        card_args = self.resolve_request_parser().parse_args()
        self.request_id = card_args["request_id"]
        self.approval = card_args["approval"]
        self.emp_id = card_args["emp_id"]

    @staticmethod
    def resolve_request_parser():
        card_request_parser = reqparse.RequestParser()
        card_request_parser.add_argument(
            "request_id", type=int, help="Card request ID is missing.", location="form", required=True
        )
        card_request_parser.add_argument(
            "approval", type=inputs.boolean, help="Request approval is missing.", location="form", required=True
        )
        card_request_parser.add_argument(
            "emp_id", type=int, help="Employee ID is missing.", location="form", required=True
        )
        return card_request_parser
