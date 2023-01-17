from flask_restx import Resource, Namespace, reqparse, abort
from flask import make_response

from server import resources


accounts_ns = Namespace("accounts", path="/accounts")
emp_accounts_ns = Namespace("employee-accounts", path="/employee/accounts")


class AccountModel:
    def __init__(self, account_id):
        self.account_id = account_id
        self.balance = float(self.get_account_info()[0])
        self.email = self.get_account_info()[1]

    def get_account_info(self):
        tup = resources.get_account_info(self.account_id)
        if len(tup):
            balance = tup[0][0]
            email = tup[0][1]
            return balance, email
        abort(400, message="Invalid account_id")

    def deposit(self, amount):
        if amount <= 0:
            print("Deposit amount should be greater than $0.")
            return False
        elif amount > 5000:
            print("Deposit amount should be less than $5000.")
            return False
        self.balance += amount
        return True

    def employee_deposit(self, amount):
        if amount <= 0:
            print("Deposit amount should be greater than $0.")
            return False
        self.balance += amount
        return True

    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount should be greater than $0.")
            return False
        elif amount > 1000:
            print("Withdrawal amount should be less than $1000.")
            return False
        elif amount > self.balance:
            print("Insufficient funds.")
            abort(403, message="Insufficient funds.")
        self.balance -= amount
        return True

    def employee_withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount should be greater than $0.")
            return False
        elif amount > self.balance:
            print("Insufficient funds.")
            abort(403, message="Insufficient funds.")
        self.balance -= amount
        return True

    def transfer_send(self, amount, destination_account):
        if amount <= 0:
            print("Sending amount should be greater than $0.")
            return False
        elif amount > 10000:
            print("Sending amount should be less than $10000.")
            return False
        elif amount > self.balance:
            print("Insufficient funds.")
            abort(403, message="Insufficient funds.")
        self.balance -= amount
        destination_account.transfer_receive(amount)
        return True

    def transfer_receive(self, amount):
        self.balance += amount
        return

    def pay(self, bill):
        if self.balance >= bill.amount:
            self.balance -= bill.amount
            # UPDATE DATABASE
            # GENERATE RECEIPT
            return True
        print("Insufficient balance.")
        return False

    def get_statement(self):
        pass


@accounts_ns.route("/deposit")
class AccountDeposit(Resource):
    @resources.token_required
    def put(self):
        acc_args = AccountArgs("amount")
        account = AccountModel(acc_args.account_id)
        obj_deposit_success = account.deposit(acc_args.amount)
        if obj_deposit_success:
            return self.__make_deposit(account.account_id, acc_args.amount, account.balance)
        abort(409, message="Invalid amount to deposit.")

    @staticmethod
    @resources.user_authorization
    def __make_deposit(account_id, amount, balance):
        db_deposit_success = resources.deposit_amount(amount, balance, account_id)
        if db_deposit_success:
            return make_response(f"${amount} deposited successfully.", 200)
        abort(500, message="Database update error.")


@accounts_ns.route("/withdraw")
class AccountWithdraw(Resource):
    @resources.token_required
    def put(self):
        acc_args = AccountArgs("amount")
        account = AccountModel(acc_args.account_id)
        obj_withdrawal_success = account.withdraw(acc_args.amount)
        if obj_withdrawal_success:
            return self.__make_withdrawal(account.account_id, acc_args.amount, account.balance)
        abort(409, message="Invalid amount to withdraw.")

    @staticmethod
    @resources.user_authorization
    def __make_withdrawal(account_id, amount, balance):
        db_withdrawal_success = resources.withdraw_amount(amount, balance, account_id)
        if db_withdrawal_success:
            return make_response(f"${amount} withdrew successfully.", 200)
        abort(500, message="Database update error.")


@accounts_ns.route("/transfer")
class AccountTransfer(Resource):
    @resources.token_required
    def get(self):
        acc_args = AccountArgs("transfer")
        rec_name = resources.get_name_from_email(acc_args.dest_email)
        if len(rec_name):
            if rec_name[0][1]:  # account is active
                resp_dict = {"response": "Success", "data": {"full_name": rec_name[0][0]}}
                return resp_dict, 200
            abort(400, message="Recipient's account is closed.")
        abort(400, message="Recipient email not found.")

    @resources.token_required
    def put(self):
        acc_args = AccountArgs("transfer")
        recipient_account_id = resources.get_account_id_with_email(acc_args.dest_email)
        if not len(recipient_account_id) or acc_args.account_id == recipient_account_id[0][0]:
            abort(400, message="Recipient email is invalid.")
        account_from = AccountModel(acc_args.account_id)
        account_to = AccountModel(recipient_account_id[0][0])
        obj_transfer_success = account_from.transfer_send(acc_args.amount, account_to)
        if obj_transfer_success:
            return self.__make_transfer(
                account_from.account_id,
                account_from.balance,
                account_from.email,
                account_to.account_id,
                account_to.balance,
                account_to.email,
                acc_args.amount
            )
        abort(409, message="Invalid amount to transfer.")

    @staticmethod
    @resources.user_authorization
    def __make_transfer(
            account_id_sender,
            account_sender_balance,
            account_sender_email,
            account_id_recipient,
            account_recipient_balance,
            account_recipient_email,
            amount):
        db_transfer_success = resources.transfer_amount(
            amount=amount,
            acc_from_id=account_id_sender,
            acc_from_balance=account_sender_balance,
            from_string=account_sender_email,
            acc_to_id=account_id_recipient,
            acc_to_balance=account_recipient_balance,
            to_string=account_recipient_email
        )
        if db_transfer_success:
            return make_response(f"Transferring ${amount} to {account_recipient_email}: Success.", 200)
        abort(500, message="Database update error.")


@accounts_ns.route("/statement")
class AccountStatement(Resource):
    @resources.token_required
    def get(self):
        acc_args = AccountArgs("statement")
        return self.__get_account_statement(acc_args.account_id)

    @staticmethod
    @resources.user_authorization
    def __get_account_statement(account_id):
        st_res = resources.get_account_statement(account_id)
        transactions = list()
        for transaction_row in range(len(st_res)):
            transaction = dict()
            transaction["type"] = st_res[transaction_row][0]
            transaction["amount"] = float(st_res[transaction_row][1])
            transaction["from_to"] = st_res[transaction_row][2]
            try:
                transaction["card"] = "*"*12 + st_res[transaction_row][3][12:]
            except TypeError:
                transaction["card"] = None
            transaction["transaction_date"] = st_res[transaction_row][4].strftime("%Y-%m-%d %H:%M:%S.%f")

            transactions.append(transaction)

        resp_dict = {"response": "Success", "data": {"transactions": transactions}}
        return resp_dict, 200


@emp_accounts_ns.route("/id")
class GetAccountWithPhone(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        phone = AccountIDArgs().phone
        account_id_resp = resources.get_account_id_with_phone(phone)
        if len(account_id_resp):
            resp = {"response": "Success", "data": {"acc_id": account_id_resp[0][0]}}
            return make_response(resp, 200)
        abort(400, message="Phone not found.")


@emp_accounts_ns.route("/info")
class GetAccountInfo(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        account_id = AccountArgs("info").account_id
        acc_situation = resources.get_account_situation(account_id)
        if len(acc_situation):
            resp = {"response": "Success", "data": {"balance": acc_situation[0][0],
                                                    "active": acc_situation[0][1],
                                                    "full_name": acc_situation[0][2]}}
            return make_response(resp, 200)
        abort(400, message="No records found.")


@emp_accounts_ns.route("/withdraw")
class AccountWithdrawEmployee(Resource):
    @resources.token_required
    def put(self):
        acc_args = AccountArgs("amount")
        account = AccountModel(acc_args.account_id)
        obj_withdrawal_success = account.employee_withdraw(acc_args.amount)
        if obj_withdrawal_success:
            return self.__make_withdrawal(account.account_id, acc_args.amount, account.balance)
        abort(409, message="Invalid amount to withdraw.")

    @staticmethod
    @resources.admin_authorization
    def __make_withdrawal(account_id, amount, balance):
        db_withdrawal_success = resources.withdraw_amount(amount, balance, account_id)
        if db_withdrawal_success:
            return make_response(f"${amount} withdrew successfully.", 200)
        abort(500, message="Database update error.")


@emp_accounts_ns.route("/deposit")
class AccountDepositEmployee(Resource):
    @resources.token_required
    def put(self):
        acc_args = AccountArgs("amount")
        account = AccountModel(acc_args.account_id)
        obj_deposit_success = account.employee_deposit(acc_args.amount)
        if obj_deposit_success:
            return self.__make_deposit(account.account_id, acc_args.amount, account.balance)
        abort(409, message="Invalid amount to deposit.")

    @staticmethod
    @resources.admin_authorization
    def __make_deposit(account_id, amount, balance):
        db_deposit_success = resources.deposit_amount(amount, balance, account_id)
        if db_deposit_success:
            return make_response(f"${amount} deposited successfully.", 200)
        abort(500, message="Database update error.")


@emp_accounts_ns.route("/close")
class AccountClose(Resource):
    @resources.token_required
    def put(self):
        acc_id = AccountArgs("close").account_id
        return self.__close_account(acc_id)

    @staticmethod
    @resources.admin_authorization
    def __close_account(account_id):
        acc_closing_success = resources.close_account(account_id)
        if acc_closing_success:
            return make_response(f"Account closed.", 200)
        abort(500, message="Database update error.")


class AccountArgs:
    def __init__(self, request_type):
        acc_parser = self.create_account_parser(request_type).parse_args()
        if request_type in ("amount", "transfer"):
            self.amount = acc_parser["amount"]
            self.dest_email = acc_parser["destination_email"] if request_type == "transfer" else None
        self.account_id = acc_parser["account_id"]

    @staticmethod
    def create_account_parser(request_type):
        account_parser = reqparse.RequestParser()
        if request_type == "amount" or request_type == "transfer":
            if request_type == "transfer":
                account_parser.add_argument(
                    "destination_email", type=str, help="Email of the recipient is required.", location="form",
                    required=True
                )
            account_parser.add_argument(
                "amount", type=float, help="Monetary amount field is required.", location="form", required=True
            )
        elif request_type not in ("statement", "info", "close"):
            raise KeyError("Invalid request type.")
        account_parser.add_argument(
            "account_id", type=int, help="ID of account is required.", location="form", required=True
        )
        return account_parser


class AccountIDArgs:
    def __init__(self):
        acc_parser = self.create_account_parser().parse_args()
        self.phone = acc_parser["phone"]

    @staticmethod
    def create_account_parser():
        account_parser = reqparse.RequestParser()
        account_parser.add_argument(
            "phone", type=str, help="Phone is required.", location="form", required=True
        )
        return account_parser


if __name__ == "__main__":
    acc = AccountModel(3)
    print(acc.balance, type(acc.balance), acc.email, type(acc.email))
