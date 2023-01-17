from flask_restx import Resource, Namespace, reqparse, abort
from flask import make_response
from werkzeug.security import check_password_hash

from server import resources

login_ns = Namespace("login")


@login_ns.route("")
class ClientLogin(Resource):
    def post(self):
        login_args = LoginArgs()
        # Check DB
        res = resources.get_password_with_username_or_client_id(login_args.username, where_column="username")
        if len(res) == 1:
            stored_pwd = res[0][0]
            if check_password_hash(stored_pwd, login_args.pwd):
                args = resources.get_login_args(login_args.username)
                if len(args) == 1:
                    args_dict = {
                        "client_id": args[0][0],
                        "account_id": args[0][1],
                        "balance": args[0][2],
                        "pronoun": args[0][3],
                        "name": args[0][4],
                        "phone": args[0][5],
                        "email": args[0][6],
                        "username": login_args.username,
                        "active": args[0][7]
                    }
                    # make personal token
                    token = resources.generate_token(args_dict["client_id"], args_dict["account_id"])
                    return make_response(
                        {
                            "data": {
                                "token": token,
                                "client_id": args_dict["client_id"],
                                "account_id": args_dict["account_id"],
                                "balance": args_dict["balance"],
                                "pronoun": args_dict["pronoun"],
                                "name": args_dict["name"],
                                "phone": args_dict["phone"],
                                "email": args_dict["email"],
                                "username": args_dict["username"],
                                "active": args_dict["active"]
                            }
                        },
                        200
                    )
                else:
                    abort(502, message="Internal error.")
            else:
                abort(401, message="Incorrect password.")
        else:
            abort(400, message="Incorrect username/password.")


@login_ns.route("/employee")
class EmployeeLogin(Resource):
    def post(self):
        login_args = LoginArgs()
        # Check DB
        res = resources.get_employee_password_with_username(login_args.username)
        if len(res) == 1:
            stored_pwd = res[0][0]
            if check_password_hash(stored_pwd, login_args.pwd):
                args = resources.get_employee_login_args(login_args.username)
                if len(args) == 1:
                    args_dict = {
                        "emp_id": args[0][0],
                        "username": args[0][1],
                        "name": args[0][2],
                        "email": args[0][3]
                    }
                    # make personal token
                    token = resources.generate_employee_token(args_dict["emp_id"])
                    return make_response(
                        {
                            "data": {
                                "token": token,
                                "emp_id": args_dict["emp_id"],
                                "name": args_dict["name"],
                                "username": args_dict["username"],
                                "email": args_dict["email"]
                            }
                        },
                        200
                    )
                else:
                    abort(502, message="Internal error.")
            else:
                abort(401, message="Incorrect password.")
        else:
            abort(400, message="Incorrect username/password.")


class LoginArgs:
    def __init__(self):
        login_args = self.create_parser().parse_args()
        self.username = login_args["username"]
        self.pwd = login_args["pwd"]

    @staticmethod
    def create_parser():
        login_parser = reqparse.RequestParser()
        login_parser.add_argument(
            "username", type=str, help="Client username required.", location="form", required=True
        )
        login_parser.add_argument(
            "pwd", type=str, help="Client password required.", location="form", required=True
        )
        return login_parser
