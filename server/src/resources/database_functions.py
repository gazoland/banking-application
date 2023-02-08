from src import resources
from src.resources.queries import ClientQueries, AccountQueries, TransactionQueries, CardQueries, EmployeeQueries, InvoiceQueries, PurchaseQueries

##### LOGIN

def get_password_with_username_or_client_id(*args, **kwargs):
    if kwargs["where_column"] == "username":
        query = ClientQueries().get_password_from_username
    elif kwargs["where_column"] == "client_id":
        query = ClientQueries().get_password_from_client_id
    else:
        raise Exception("where_column [username, client_id] is required.")
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(query, args)
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_login_args(username):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_login_args, (username,))
    args = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return args


def get_employee_password_with_username(username):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(EmployeeQueries().get_password_from_username, (username,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_employee_login_args(username):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(EmployeeQueries().get_login_args, (username,))
    args = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return args


##### CLIENT

def update_client_password(new_pwd, client_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().update_password_with_client_id, (new_pwd,client_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_username(username):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_username, (username,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def update_username(new_username, client_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().update_username, (new_username, client_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result



def get_client_name_with_account_id(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_client_name_with_account_id, (account_id,))
    args = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return args


def get_name_from_email(email):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_full_name, (email,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_email(email):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_email, (email,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def update_email(new_email, client_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().update_email, (new_email, client_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_phone(phone):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_phone, (phone,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def update_phone(new_phone, client_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().update_phone, (new_phone, client_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_pronoun_id(pronoun_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_pronoun_id, (pronoun_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def update_pronoun_id(new_pronoun_id, client_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().update_pronoun_id, (new_pronoun_id, client_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_client_id(username):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(ClientQueries().get_client_id, (username,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def register_client(username, full_name, dob, email, pwd, phone, pronoun_id, acc_number, deposit):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    result = False
    # Register client
    cursor.execute(ClientQueries().register_new_client, (username, full_name, dob, email, pwd, phone, pronoun_id))
    if cursor.rowcount == 1:
        # Register account
        cursor.execute(ClientQueries().get_client_id, (username,))
        client_id = cursor.fetchall()[0][0]
        cursor.execute(AccountQueries().create_account, (acc_number, client_id, deposit, True))
        if cursor.rowcount == 1:
            db_conn.commit()
            result = True
    cursor.close()
    db_conn.close()
    return result


##### ACCOUNT

def get_account_info(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_account_info, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def deposit_amount(amount, new_balance, account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().update_balance, (new_balance, account_id))
    if cursor.rowcount == 1:
        cursor.execute(TransactionQueries().create_transaction, (account_id, 'deposit', amount, None))
        if cursor.rowcount == 1:
            db_conn.commit()
            result = True
        else:
            result = False
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def withdraw_amount(amount, new_balance, account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().update_balance, (new_balance, account_id))
    if cursor.rowcount == 1:
        cursor.execute(TransactionQueries().create_transaction, (account_id, 'withdraw', amount, None))
        if cursor.rowcount == 1:
            db_conn.commit()
            result = True
        else:
            result = False
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_account_id_with_phone(phone):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_id_with_phone, (phone,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_account_id_with_email(email):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_id_with_email, (email,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res

def transfer_amount(amount, acc_from_id, acc_from_balance, from_string, acc_to_id, acc_to_balance, to_string):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().update_balance, (acc_from_balance, acc_from_id))
    send = cursor.rowcount
    cursor.execute(AccountQueries().update_balance, (acc_to_balance, acc_to_id))
    receive = cursor.rowcount
    if send and receive:
        cursor.execute(TransactionQueries().create_transaction, (acc_from_id, 'send', amount, to_string))
        trans_send = cursor.rowcount
        cursor.execute(TransactionQueries().create_transaction, (acc_to_id, 'receive', amount, from_string))
        trans_receive = cursor.rowcount
        if trans_send and trans_receive:
            db_conn.commit()
            result = True
        else:
            result = False
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_account_statement(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_statement, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def create_account(acc_number, client_id, balance):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().create_account, (acc_number, client_id, balance, True))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_max_account_number():
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_max_account)
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_account_situation(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().get_account_situation, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def close_account(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(AccountQueries().close_account, (False, account_id))
    result = False
    if cursor.rowcount:
        cursor.execute(CardQueries().deactivate_all_account_cards, (False, account_id))
        if cursor.rowcount:
            db_conn.commit()
            result = True
    cursor.close()
    db_conn.close()
    return result


##### CARDS

def get_deactivated_card(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_deactivated_card, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def activate_card(activation_code, card_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().activate_card, (True, activation_code, card_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def make_card_request(account_id, brand_id, category_id, card_type):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().make_card_request, (account_id, brand_id, category_id, card_type, True, False))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_card_list(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_all_cards, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_payable_statements_list(account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_payable_statements, (account_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_paying_statement_info(card_id, statement_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_statement_info, (statement_id, card_id))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def pay_card_statement(account_id, card_id, statement_id, new_balance, amount):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    # Pay
    cursor.execute(AccountQueries().update_balance, (new_balance, account_id))
    paid = cursor.rowcount
    # Register transaction
    cursor.execute(TransactionQueries().create_transaction, (account_id, 'payment', amount, 'CREDIT CARD STATEMENT'))
    transaction = cursor.rowcount
    # Update invoice
    cursor.execute(InvoiceQueries().pay_statement, (statement_id, card_id))
    invoice_update = cursor.rowcount
    if paid and transaction and invoice_update:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def change_card_lock(account_id, card_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().lock_unlock, (account_id, card_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_all_card_statements(card_id, account_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_all_card_statements, (card_id, account_id))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_card_statement(account_id, card_id, statement_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_statement, (statement_id, card_id, account_id))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_card_pin(account_id, card_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_pin, (account_id, card_id))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def update_card_pin(account_id, card_id, new_pin):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().update_pin, (new_pin, account_id, card_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def update_card_statement_day(account_id, card_id, new_day):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().update_statement_day, (new_day, account_id, card_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def update_card_limit(account_id, card_id, new_limit):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().update_limit, (new_limit, account_id, card_id))
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def create_new_card(
        account_id,
        card_number,
        card_name,
        sec_code,
        pin,
        exp_date,
        activation_code,
        card_type,
        brand_id,
        category_id,
        limit
    ):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(
        CardQueries().create_new_card,
        (
            account_id,
            card_number,
            card_name,
            sec_code,
            pin,
            exp_date,
            card_type,
            brand_id,
            category_id,
            False,
            activation_code,
            True,
            '05',
            limit
        )
    )
    if cursor.rowcount == 1:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def get_card_requests():
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().get_card_requests)
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


##### EMPLOYEE


def get_employee_name_with_id(emp_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(EmployeeQueries().get_emp_name_with_id, (emp_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def deny_card_request(request_id, emp_name):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(EmployeeQueries().deny_card_request, (emp_name, request_id))
    if cursor.rowcount:
        db_conn.commit()
        result = True
    else:
        result = False
    cursor.close()
    db_conn.close()
    return result


def approve_card_request(
        account_id,
        card_number,
        card_name,
        sec_code,
        pin,
        exp_date,
        card_type,
        brand_id,
        category_id,
        activation_code,
        statement_day,
        limit,
        emp_name,
        request_id
    ):

    result = False
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(CardQueries().create_new_card, (
            account_id, card_number, card_name, sec_code, pin, exp_date, card_type, brand_id, category_id, False,
            activation_code, True, statement_day, limit
    ))
    card_created = cursor.rowcount
    cursor.execute(EmployeeQueries().approve_card_request, (emp_name, request_id))
    request_updated = cursor.rowcount
    if card_created and request_updated:
        db_conn.commit()
        result = True
    cursor.close()
    db_conn.close()
    return result


def get_new_card_request_info(request_id):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(EmployeeQueries().get_new_card_request_info, (request_id,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


##### PURCHASES


def get_card_purchase_request_info(card_number):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(PurchaseQueries().get_card_purchase_request_info, (card_number,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_acc_purchase_request_info(card_number):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(PurchaseQueries().get_acc_purchase_request_info, (card_number,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def get_statement_purchase_request_info(card_number):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    cursor.execute(PurchaseQueries().get_statement_purchase_request_info, (card_number,))
    res = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return res


def register_purchase(purchase_args, card_args, acc_args, new_balance):
    db_conn = resources.connect_to_database()
    cursor = db_conn.cursor()
    res = False
    if purchase_args.pay_type == "credit":
        cursor.execute(PurchaseQueries().create_credit_purchase, (card_args["card_id"],
                                                                  acc_args["invoice_id"],
                                                                  purchase_args.est_code,
                                                                  purchase_args.est_location,
                                                                  purchase_args.purchase_total))
        if cursor.rowcount:
            db_conn.commit()
            res = True

    else:
        cursor.execute(PurchaseQueries().create_debit_purchase, (acc_args["account_id"],
                                                                 card_args["card_id"],
                                                                 purchase_args.purchase_total,
                                                                 f"{purchase_args.est_code} "
                                                                 f"{purchase_args.est_location}"))
        purchase_made = cursor.rowcount

        cursor.execute(AccountQueries().update_balance, (new_balance, acc_args["account_id"]))
        balance_updated = cursor.rowcount

        if purchase_made and balance_updated:
            db_conn.commit()
            res = True

    cursor.close()
    db_conn.close()
    return res


if __name__ == "__main__":
    user = get_username('amy')
    print(user)
    print(len(user))
    if not len(user):
        print('dfdf')
