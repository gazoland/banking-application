from client.employee.src.employee_login import Login, LoginMenu

def main():
    login, data = False, None
    while not login:
        login, data = Login().login_attempt()
    no_exit = True
    while no_exit:
        no_exit = LoginMenu(
            token = data["token"],
            emp_id=data["emp_id"],
            name=data["name"],
            email=data["email"],
            username=data["username"]
        ).execute()
    print("Logout successful. See you later!")


if __name__ == "__main__":
    main()
