import os
import sys
sys.path.append(os.getcwd() + "/client")

from src.client_login import Login, LoginMenu, InactiveAccount

def main():
    login, data = False, None
    while not login:
        login, data = Login().login_attempt()
    no_exit = True
    while no_exit:
        if data["active"]:
            no_exit = LoginMenu(
                token = data["token"],
                client_id=data["client_id"],
                account_id=data["account_id"],
                balance=float(data["balance"]),
                pronoun=data["pronoun"],
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                username=data["username"]
            ).execute()
        else:
            no_exit = InactiveAccount(
                pronoun=data["pronoun"],
                name=data["name"]
            ).execute()
    print("Logout successful. See you later!")


if __name__ == "__main__":
    main()
