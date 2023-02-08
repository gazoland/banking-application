from datetime import datetime, timedelta
from flask import current_app, abort
from flask_restx.reqparse import RequestParser
from functools import wraps
import jwt

def generate_token(client_id, account_id):
    token = jwt.encode(
        {
            "user": client_id,
            "id": account_id,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        },
        current_app.config["SECRET_KEY"]
    )
    return token


def generate_employee_token(emp_id):
    token = jwt.encode(
        {
            "id": emp_id,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        },
        current_app.config["SECRET_KEY"]
    )
    return token


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = TokenArg().value
        try:
            jwt.decode(token, current_app.config["SECRET_KEY"], "HS256")
            return f(*args, **kwargs)
        except jwt.exceptions.InvalidSignatureError:
            abort(401, "Token authentication failed.")
        except jwt.exceptions.ExpiredSignatureError:
            abort(401, "Token authentication failed. Token expired.")

    return wrapper


def user_authorization(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = TokenArg().value
        auth = AuthorizationArg()
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], "HS256")
            if auth.client_id != -1:
                if data["user"] != auth.client_id:
                    abort(403, "Unauthorized user.")
            elif auth.account_id != -1:
                if data["id"] != auth.account_id:
                    abort(403, "Unauthorized id.")
            elif auth.account_id == auth.client_id == -1:
                abort(403, "Authorization failed. User or ID value required.")

            return f(*args, **kwargs)

        except jwt.exceptions.InvalidSignatureError:
            abort(401, "Token authentication failed.")
        except jwt.exceptions.ExpiredSignatureError:
            abort(401, "Token authentication failed. Token expired.")

    return wrapper


def admin_authorization(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = TokenArg().value
        auth = AdminAuthorizationArg()
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], "HS256")
            if auth.emp_id != data["id"]:
                abort(403, "Unauthorized employee.")

            return f(*args, **kwargs)

        except jwt.exceptions.InvalidSignatureError:
            abort(401, "Token authentication failed.")
        except jwt.exceptions.ExpiredSignatureError:
            abort(401, "Token authentication failed. Token expired.")

    return wrapper


class TokenArg:
    def __init__(self):
        token_args = self.create_parser().parse_args()
        authentication_header = token_args["Authorization"].split(" ")
        try:
            self.value = authentication_header[1]
        except IndexError:
            abort(400, "Invalid Bearer token.")

    @staticmethod
    def create_parser():
        token_parser = RequestParser()
        token_parser.add_argument(
            "Authorization", type=str, help="Authentication token required.", location="headers", required=True
        )
        return token_parser


class AuthorizationArg:
    def __init__(self):
        auth_args = self.create_parser().parse_args()
        if auth_args["client_id"] is None and auth_args["account_id"] is None:
            abort(403, "Authorization failed. Failed to provide User or ID.")
        self.client_id = auth_args["client_id"] if auth_args["client_id"] is not None else -1
        self.account_id = auth_args["account_id"] if auth_args["account_id"] is not None else -1

    @staticmethod
    def create_parser():
        auth_parser = RequestParser()
        auth_parser.add_argument(
            "account_id", type=int, help="ID value required.", location="form", required=False
        )
        auth_parser.add_argument(
            "client_id", type=int, help="User value required.", location="form", required=False
        )
        return auth_parser


class AdminAuthorizationArg:
    def __init__(self):
        auth_args = self.create_parser().parse_args()
        self.emp_id = auth_args["emp_id"]

    @staticmethod
    def create_parser():
        auth_parser = RequestParser()
        auth_parser.add_argument(
            "emp_id", type=int, help="Admin ID value required.", location="form", required=True
        )
        return auth_parser


if __name__ == "__main__":
    a = generate_token(123)
    print(a)
