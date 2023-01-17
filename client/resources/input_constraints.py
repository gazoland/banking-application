import re


class ConstraintResponse:
    def __init__(self):
        self.message = ""
        self.valid = False


def new_password_check(new_pwd):
    res = ConstraintResponse()
    if len(new_pwd) < 8:
        res.message = "Password must be at least 8 digits."
        return res

    capitals, digits, lowers, symbols = False, False, False, False
    for char in new_pwd:
        if char.isdigit():
            digits = True
        elif char.islower():
            lowers = True
        elif char.isupper():
            capitals = True
        elif char in "!@#$%&?.-_+=":
            symbols = True
    if digits and capitals and lowers and symbols:
        res.valid = True
        return res
    else:
        res.message = "Password must contain at least:\n" \
                      "- 1 upper letter;\n" \
                      "- 1 lower letter;\n" \
                      "- 1 digit;\n" \
                      "- 1 symbol among ! @ # $ % & ? . + - _ ="
        return res


def new_username_check(new_user):
    res = ConstraintResponse()
    if len(new_user) < 6:
        res.message = "Username must be at least 6 digits."
        return res

    if len(new_user) > 25:
        res.message = "Username must be shorter than 26 digits."
        return res

    if not all(((x.isalnum() or x.islower() or x in '._-') for x in new_user)):
        res.message = 'Usernames must contain only lower letters, numbers or the symbols: "-", "_", "."'
        return res

    if sum(c.isalpha() for c in new_user) < 3:
        res.message = "Username must contain at least 3 letters."
        return res

    res.valid = True
    return res


def new_email_check(new_email):
    res = ConstraintResponse()
    if not re.match("([A-Za-z0-9]+[._-]*[A-Za-z0-9]*)+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", new_email):
        res.message = "Please type a valid email address."
        return res
    res.valid = True
    return res


def new_phone_check(new_phone):
    res = ConstraintResponse()
    if len(new_phone) < 9 or len(new_phone) > 11 or not new_phone.isdigit():
        res.message = "Please type a valid phone number."
        return res
    res.valid = True
    return res


def new_dob_check(dob):
    res = ConstraintResponse()
    if re.match("\d{2}/\d{2}/\d{4}", dob):
        if 0 < int(dob.split("/")[0]) <= 12 and \
        0 < int(dob.split("/")[1]) <= 31 and \
        1920 < int(dob.split("/")[2]) <= 2008:
            res.valid = True
            return res
    res.message = "Please type a valid date."
    return res


def valid_amount_check(amount:str):
    res = ConstraintResponse()
    try:
        float(amount)
    except ValueError:
        res.message = 'Please enter a valid amount. Use "." instead of "," to separate cents.'
        return res
    if sum(c == '.' for c in amount) > 1:
        res.message = 'Please enter a valid amount with a "." separating the cents.'
        return res
    if "." in amount and len(amount.split(".")[1]) > 2:
        res.message = 'Please enter an amount with up to 2 digits in the cents.'
        return res
    res.valid = True
    return res


def valid_card_number_check(card_number:str):
    res = ConstraintResponse()
    if len(card_number) != 16:
        res.message = "Invalid card number. It must be 16 digits long."
        return res
    if not all(x.isdigit() for x in card_number):
        res.message = "Invalid card number. Please type in only digits."
        return res
    res.valid = True
    return res


def valid_card_sec_code_check(card_sec_code:str):
    res = ConstraintResponse()
    if len(card_sec_code) != 3:
        res.message = "Invalid security code. It must be 3 digits long."
        return res
    if not all(x.isdigit() for x in card_sec_code):
        res.message = "Invalid security code. Please type in only digits."
        return res
    try:
        int(card_sec_code)
    except ValueError:
        res.message = "Invalid security code."
        return res
    res.valid = True
    return res


def valid_card_exp_date_check(exp_date:str):
    res = ConstraintResponse()
    if re.match("\d{2}/\d{4}", exp_date):
        if 0 < int(exp_date.split("/")[0]) <= 12 and 1900 < int(exp_date.split("/")[1]) <= 2100:
            res.valid = True
            return res
    res.message = "Please type a valid expiration date."
    return res


def valid_card_pin_check(card_pin:str):
    res = ConstraintResponse()
    if len(card_pin) != 4:
        res.message = "Invalid PIN. It must be 4 digits long."
        return res
    if not all(x.isdigit() for x in card_pin):
        res.message = "Invalid PIN. Please type in only digits."
        return res
    res.valid = True
    return res


if __name__ == "__main__":
    print(new_dob_check('12/31/2006').valid)
