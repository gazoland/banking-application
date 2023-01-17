from flask_restx import Resource, Namespace, reqparse, abort
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash

from server import resources


clients_ns = Namespace("clients", path="/clients")
emp_clients_ns = Namespace("employee-clients", path="/employee/clients")


@clients_ns.route("/password")
class ClientUpdatePassword(Resource):
    @resources.token_required
    def put(self):
        client_args = ClientArgs()

        return self.__update_password(
            client_id=client_args.client_id,
            old_pwd=client_args.old_value,
            new_pwd=client_args.new_value
        )

    @staticmethod
    @resources.user_authorization
    def __update_password(client_id, old_pwd, new_pwd):
        stored_pwd = resources.get_password_with_username_or_client_id(client_id, where_column="client_id")[0][0]
        if check_password_hash(stored_pwd, old_pwd):
            new_pwd_hash = generate_password_hash(new_pwd)
            successful_update = resources.update_client_password(new_pwd_hash, client_id)
            if successful_update:
                return make_response(
                    "Success.", 200
                )
            else:
                abort(500, message="Database update error.")
        else:
            abort(409, message="Current password is incorrect.")


@clients_ns.route("/email")
class ClientUpdateEmail(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        client_args = ClientArgs()
        existing_email = resources.get_email(client_args.new_value)
        resp_dict = {"response": "Success", "data": {"valid_email": False}}
        if not len(existing_email):
            resp_dict["data"]["valid_email"] = True
        return resp_dict, 200

    @resources.token_required
    def put(self):
        client_args = ClientArgs()
        return self.__update_email(client_args.client_id, client_args.new_value)

    @staticmethod
    @resources.user_authorization
    def __update_email(client_id, new_email):
        check_existing_email = resources.get_email(new_email)
        if not len(check_existing_email):
            successful_update = resources.update_email(new_email, client_id)
            if successful_update:
                return make_response(
                    "Success.", 200
                )
            else:
                abort(500, message="Database update error.")
        else:
            abort(409, message="Email already taken.")


@clients_ns.route("/phone")
class ClientUpdatePhone(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        client_args = ClientArgs()
        existing_phone = resources.get_phone(client_args.new_value)
        resp_dict = {"response": "Success", "data": {"valid_phone": False}}
        if not len(existing_phone):
            resp_dict["data"]["valid_phone"] = True
        return resp_dict, 200

    @resources.token_required
    def put(self):
        client_args = ClientArgs()
        return self.__update_phone(client_args.client_id, client_args.new_value)

    @staticmethod
    @resources.user_authorization
    def __update_phone(client_id, new_phone):
        check_existing_phone = resources.get_phone(new_phone)
        if not len(check_existing_phone):
            successful_update = resources.update_phone(new_phone, client_id)
            if successful_update:
                return make_response(
                    "Success.", 200
                )
            else:
                abort(500, message="Database update error.")
        else:
            abort(409, message="Phone already taken.")


@clients_ns.route("/username")
class ClientUpdateUsername(Resource):
    @resources.token_required
    @resources.admin_authorization
    def get(self):
        client_args = ClientArgs()
        existing_username = resources.get_username(client_args.new_value)
        resp_dict = {"response": "Success", "data": {"valid_username": False}}
        if not len(existing_username):
            resp_dict["data"]["valid_username"] = True
        return resp_dict, 200

    @resources.token_required
    def put(self):
        client_args = ClientArgs()
        return self.__update_username(client_args.client_id, client_args.new_value)

    @staticmethod
    @resources.user_authorization
    def __update_username(client_id, new_username):
        check_existing_username = resources.get_username(new_username)
        if not len(check_existing_username):
            successful_update = resources.update_username(new_username, client_id)
            if successful_update:
                return make_response(
                    "Success.", 200
                )
            else:
                abort(500, message="Database update error.")
        else:
            abort(409, message="Username already taken.")


@clients_ns.route("/pronoun")
class ClientUpdatePronoun(Resource):
    @resources.token_required
    def put(self):
        client_args = ClientArgs()
        return self.__update_pronoun(client_args.client_id, int(client_args.new_value))

    @staticmethod
    @resources.user_authorization
    def __update_pronoun(client_id, new_pronoun_id):
        check_existing_pronoun_id = resources.get_pronoun_id(new_pronoun_id)
        if len(check_existing_pronoun_id):
            successful_update = resources.update_pronoun_id(new_pronoun_id, client_id)
            if successful_update:
                return make_response(
                    "Success.", 200
            )
            else:
                abort(500, message="Database update error.")
        else:
            abort(409, message="Invalid pronoun_id.")


@emp_clients_ns.route("/new")
class ClientRegister(Resource):
    @resources.token_required
    def post(self):
        client_args = ClientRegistryArgs()
        return self.__post_new_client(
            client_args.username,
            client_args.full_name,
            client_args.dob,
            client_args.email,
            client_args.pwd,
            client_args.phone,
            client_args.pronoun_id,
            client_args.deposit
        )

    @staticmethod
    @resources.admin_authorization
    def __post_new_client(username, full_name, dob, email, pwd, phone, pronoun_id, deposit):
        existing_username = resources.get_username(username)
        existing_email = resources.get_email(email)
        existing_phone = resources.get_phone(phone)
        if not len(existing_username) and not len(existing_email) and not len(existing_phone):
            # Register client
            acc_number = resources.get_max_account_number()[0][0] + 1
            pwd_hash = generate_password_hash(pwd)
            successful_registry = resources.register_client(
                username, full_name, dob, email, pwd_hash, phone, pronoun_id, acc_number, deposit
            )
            if successful_registry:
                acc_id = resources.get_account_id_with_phone(phone)
                resp = {"response": "Success", "data": {"acc_id": acc_id}}
                return make_response(resp, 200)
            else:
                abort(500, message="Database error.")
        else:
            existing_fields = {len(existing_username): "username",
                               len(existing_email): "email",
                               len(existing_phone): "phone"}
            str_field = existing_fields[1]
            abort(409, message=f"Invalid {str_field}. It already exists in the database.")


class ClientArgs:
    def __init__(self):
        client_args = self.create_parser().parse_args()
        self.new_value = client_args["new_value"]
        self.old_value = client_args["old_value"]
        self.client_id = client_args["client_id"]

    @staticmethod
    def create_parser():
        client_parser = reqparse.RequestParser()
        client_parser.add_argument(
            "new_value", type=str, help="New value of the field to update required.", location="form", required=True
        )
        client_parser.add_argument(
            "old_value", type=str, help="Curent value of the field to update required.", location="form", required=True
        )
        client_parser.add_argument(
            "client_id", type=int, help="Client ID is required.", location="form", required=True
        )
        return client_parser


class ClientRegistryArgs:
    def __init__(self):
        client_args = self.create_parser().parse_args()
        self.username = client_args["username"]
        self.full_name = client_args["full_name"]
        self.dob = client_args["dob"]
        self.email = client_args["email"]
        self.pwd = client_args["pwd"]
        self.phone = client_args["phone"]
        self.pronoun_id = client_args["pronoun_id"]
        self.deposit = client_args["deposit"]

    @staticmethod
    def create_parser():
        client_parser = reqparse.RequestParser()
        client_parser.add_argument(
            "username", type=str, help="Client's username required.", location="form", required=True
        )
        client_parser.add_argument(
            "full_name", type=str, help="Client's full name required.", location="form", required=True
        )
        client_parser.add_argument(
            "dob", type=str, help="Client's date of birth required.", location="form", required=True
        )
        client_parser.add_argument(
            "email", type=str, help="Client's email required.", location="form", required=True
        ),
        client_parser.add_argument(
            "pwd", type=str, help="Client's password required.", location="form", required=True
        ),
        client_parser.add_argument(
            "phone", type=str, help="Client's phone required.", location="form", required=True
        ),
        client_parser.add_argument(
            "pronoun_id", type=int, help="Client's pronoun required.", location="form", required=True
        ),
        client_parser.add_argument(
            "deposit", type=float, help="Client's initial deposit required.", location="form", required=True
        )
        return client_parser
