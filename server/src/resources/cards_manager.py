from random import choice
from datetime import datetime
from dateutil import relativedelta


def generate_card_args(full_name, pin, card_type, category_id):
    card_number = generate_card_numbers("card_number")
    sec_code = generate_card_numbers("sec_code")
    card_name = full_name.split(" ")[0].upper() + " " +  full_name.split(" ")[-1].upper()
    exp_date = datetime.now().date() + relativedelta.relativedelta(years=5)
    exp_date = exp_date.replace(day=1)
    activation_code = generate_card_numbers("activation_code")
    limit = choose_card_limit(card_type, category_id)
    if pin is None:
        pin = generate_card_numbers("pin")

    args = {
        "card_number": card_number,
        "sec_code": sec_code,
        "card_name": card_name,
        "exp_date": exp_date,
        "activation_code": activation_code,
        "pin": pin,
        "limit": limit
    }

    return args

def generate_card_numbers(arg):
    ref = {
        "card_number": 16,
        "sec_code": 3,
        "activation_code": 6,
        "pin": 4
    }
    number = "".join([choice("0123456789") for _ in range(ref[arg])])
    if arg == "card_number" and number[0] == "0":
        number = "5" + number[1:]
    return number


def choose_card_limit(card_type, category_id):
    limit_ref = {
        1: 600,  # Silver
        2: 2000,  # Gold
        3: 8000,  # Platinum
        4: 20000  # Black
    }
    if card_type == "debit":
        return None
    return limit_ref[category_id]


if __name__ == "__main__":
    generate_card_numbers()
