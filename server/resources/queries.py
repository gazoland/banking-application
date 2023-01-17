class AccountQueries:
    @property
    def create_account(self):
        query = """
            INSERT INTO bank.accounts (acc_number, client_id, balance, dt_open, active)
            VALUES (%s, %s, %s, now(), %s);
        """
        return query

    @property
    def update_balance(self):
        query = """
            UPDATE bank.accounts 
            SET balance = %s
            WHERE id = %s;
        """
        return query

    @property
    def get_account_info(self):
        query = """
            SELECT a.balance, c.email 
            FROM bank.accounts a
            INNER JOIN bank.clients c ON a.client_id = c.id
            WHERE a.id = %s;
        """
        return query

    @property
    def get_id_with_phone(self):
        query = """
            SELECT a.id 
            FROM bank.accounts a
            INNER JOIN bank.clients c ON a.client_id = c.id
            WHERE c.phone = %s;
        """
        return query

    @property
    def get_id_with_email(self):
        query = """
            SELECT a.id 
            FROM bank.accounts a
            INNER JOIN bank.clients c ON a.client_id = c.id
            WHERE c.email = %s;
        """
        return query

    @property
    def close_account(self):
        query = """
            UPDATE bank.accounts
            SET active = %s, dt_close = now()
            WHERE id = %s;
        """
        return query

    @property
    def get_statement(self):
        query = """
            SELECT t.type, t.amount, t.from_to, c.card_number, t.dt_created
            FROM bank.transactions t
            LEFT JOIN bank.cards c ON t.card_id = c.id
            WHERE t.account_id = %s
            ORDER BY t.dt_created DESC;
        """
        return query

    @property
    def get_max_account(self):
        query = """
            SELECT max(acc_number)
            FROM bank.accounts;
        """
        return query

    @property
    def get_account_situation(self):
        query = """
            SELECT a.balance, a.active, c.full_name 
            FROM bank.accounts a
            INNER JOIN bank.clients c ON a.client_id = c.id
            WHERE a.id = %s;
        """
        return query


class ClientQueries:
    @property
    def get_password_from_username(self):
        query = """
            SELECT pwd
            FROM bank.clients
            WHERE username = %s;
        """
        return query

    @property
    def get_personal_token_from_client_id(self):
        query = """
            SELECT personal_token
            FROM bank.clients
            WHERE id = %s;
        """
        return query

    @property
    def get_password_from_client_id(self):
        query = """
            SELECT pwd
            FROM bank.clients
            WHERE id = %s;
        """
        return query

    @property
    def get_client_name_with_account_id(self):
        query = """
            SELECT c.full_name
            FROM bank.clients c 
            INNER JOIN bank.accounts a ON c.id = a.client_id
            WHERE a.id = %s;
        """
        return query

    @property
    def get_login_args(self):
        query = """
            SELECT 
                c.id AS client_id, 
                a.id, 
                a.balance, 
                p.pronoun, 
                c.full_name,
                c.phone,
                c.email,
                a.active
            FROM bank.clients c
            INNER JOIN bank.accounts a ON c.id = a.client_id
            INNER JOIN bank.treatment_pronouns p ON c.pronoun_id = p.id
            WHERE c.username = %s;
        """
        return query

    @property
    def get_username(self):
        query = """
            SELECT username 
            FROM bank.clients
            WHERE username = %s;
        """
        return query

    @property
    def update_username(self):
        query = """
            UPDATE bank.clients
            SET username = %s, dt_updated = NOW()
            WHERE id = %s;
        """
        return query

    @property
    def get_full_name(self):
        query = """
            SELECT c.full_name, a.active
            FROM bank.clients c
            INNER JOIN bank.accounts a ON c.id = a.client_id
            WHERE email = %s;
        """
        return query

    @property
    def get_email(self):
        query = """
            SELECT email 
            FROM bank.clients
            WHERE email = %s;
        """
        return query

    @property
    def update_email(self):
        query = """
            UPDATE bank.clients
            SET email = %s, dt_updated = NOW()
            WHERE id = %s;
        """
        return query

    @property
    def update_password_with_client_id(self):
        query = """
            UPDATE bank.clients
            SET pwd = %s, dt_updated = NOW()
            WHERE id = %s;
        """
        return query

    @property
    def get_phone(self):
        query = """
            SELECT phone
            FROM bank.clients
            WHERE phone = %s;
        """
        return query

    @property
    def update_phone(self):
        query = """
            UPDATE bank.clients
            SET phone = %s, dt_updated = NOW()
            WHERE id = %s;
        """
        return query

    @property
    def get_pronoun_id(self):
        query = """
            SELECT id
            FROM bank.treatment_pronouns
            WHERE id = %s;
        """
        return query

    @property
    def update_pronoun_id(self):
        query = """
            UPDATE bank.clients
            SET pronoun_id = %s, dt_updated = NOW()
            WHERE id = %s;
        """
        return query

    @property
    def get_client_id(self):
        query = """
                SELECT id
                FROM bank.clients
                WHERE username = %s;
            """
        return query

    @property
    def register_new_client(self):
        query = """
            INSERT INTO bank.clients 
            (username, full_name, dob, email, pwd, phone, pronoun_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        return query


class CardQueries:
    @property
    def get_deactivated_card(self):
        query = """
            SELECT id, activation_code
            FROM bank.cards
            WHERE account_id = %s
            AND active = false;
        """
        return query

    @property
    def activate_card(self):
        query = """
            UPDATE bank.cards
            SET active = %s
            WHERE activation_code = %s
            AND id = %s;
        """
        return query

    @property
    def deactivate_all_account_cards(self):
        query = """
            UPDATE bank.cards
            SET active = %s
            WHERE account_id = %s;
        """
        return query

    @property
    def make_card_request(self):
        query = """
            INSERT INTO bank.card_requests (account_id, brand_id, category_id, type, pending, approved)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        return query

    @property
    def get_all_cards(self):
        query = """
            SELECT 
                c.id,
                c.card_number, 
                c.type, 
                cb.brand_name,
                cc.category,
                c.unlocked,
                c.statement_day, 
                c.current_limit
            FROM bank.cards c
            INNER JOIN bank.card_brands cb ON c.brand_id = cb.id
            INNER JOIN bank.card_categories cc ON c.brand_id = cc.id
            WHERE account_id = %s
            ORDER BY c.exp_date ASC;
        """
        return query

    @property
    def get_payable_statements(self):
        query = """
            SELECT i.dt_start, i. dt_end, i.dt_due, i.status, i.total, i.id, i.card_id
            FROM bank.invoices i
            INNER JOIN bank.cards c ON i.card_id = c.id 
            WHERE c.account_id = %s
            AND i.status IN ('open', 'closed', 'overdue');
        """
        return query

    @property
    def lock_unlock(self):
        query = """
            UPDATE bank.cards
            SET unlocked = not unlocked
            WHERE account_id = %s
            AND id = %s;
        """
        return query

    @property
    def get_all_card_statements(self):
        query = """
            SELECT i.dt_start, i.dt_end, i.status, i.total, i.id
            FROM bank.invoices i
            INNER JOIN bank.cards c ON i.card_id = c.id
            WHERE i.card_id = %s
            AND c.account_id = %s;
        """
        return query

    @property
    def get_statement_info(self):
        query = """
            SELECT total
            FROM bank.invoices
            WHERE id = %s
            AND card_id = %s
        """
        return query

    @property
    def get_statement(self):
        query = """
            SELECT p.amount, p.establishment, p.location, p.purchase_status, p.dt_created
            FROM bank.purchases p
            INNER JOIN bank.cards c ON p.card_id = c.id
            INNER JOIN bank.invoices i ON p.invoice_id = i.id
            WHERE i.id = %s
            AND c.id = %s
            AND c.account_id = %s;
        """
        return query

    @property
    def get_pin(self):
        query = """
            SELECT pin
            FROM bank.cards
            WHERE account_id = %s
            AND id = %s;
        """
        return query

    @property
    def update_pin(self):
        query = """
            UPDATE bank.cards
            SET pin = %s
            WHERE account_id = %s
            AND id = %s;
        """
        return query

    @property
    def update_statement_day(self):
        query = """
            UPDATE bank.cards
            SET statement_day = %s
            WHERE account_id = %s
            AND id = %s;
        """
        return query

    @property
    def update_limit(self):
        query = """
            UPDATE bank.cards
            SET current_limit = %s
            WHERE account_id = %s
            AND id = %s;
        """
        return query

    @property
    def create_new_card(self):
        query = """
            INSERT INTO bank.cards (
                account_id,
                card_number, 
                card_name, 
                security_code, 
                pin, 
                exp_date, 
                type, 
                brand_id, 
                category_id, 
                active, 
                activation_code, 
                unlocked, 
                statement_day, 
                current_limit
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        return query

    @property
    def get_card_requests(self):
        query = """
            WITH total_cards AS (
                SELECT COUNT(id) as total, account_id
                FROM bank.cards
                GROUP BY account_id
            ),
            late_invoices AS (
                SELECT COUNT(id) as total, card_id
                FROM bank.invoices
                WHERE dt_paid > dt_due
                GROUP BY card_id
            )
            SELECT 
                r.id, 
                r.dt_created,
                a.balance,
                cb.brand_name,
                cc.category,
                r.type,
                tc.total as total_cards,
                li.total as total_late_invoices
            FROM bank.card_requests r
            INNER JOIN bank.accounts a ON r.account_id = a.id
            INNER JOIN bank.cards c ON a.id = c.account_id
            INNER JOIN bank.card_brands cb ON r.brand_id = cb.id
            INNER JOIN bank.card_categories cc ON r.category_id = cc.id
            INNER JOIN total_cards tc ON a.id = tc.account_id
            LEFT JOIN late_invoices li ON c.id = li.card_id
            WHERE pending IS true
            ORDER BY r.dt_created ASC; 
        """
        return query


class EmployeeQueries:
    @property
    def get_password_from_username(self):
        query = """
            SELECT pwd
            FROM bank.employees
            WHERE username = %s;
        """
        return query

    @property
    def get_login_args(self):
        query = """
            SELECT 
                id, 
                username,
                full_name,
                email
            FROM bank.employees
            WHERE username = %s;
        """
        return query

    @property
    def get_emp_name_with_id(self):
        query = """
            SELECT full_name
            FROM bank.employees
            WHERE id = %s
        """
        return query

    @property
    def deny_card_request(self):
        query = """
            UPDATE bank.card_requests
            SET 
                pending = false, 
                dt_approved_denied = now(),
                decision_by = %s
            WHERE id = %s; 
        """
        return query

    @property
    def approve_card_request(self):
        query = """
            UPDATE bank.card_requests
            SET 
                pending = false, 
                approved = true,
                dt_approved_denied = now(),
                decision_by = %s
            WHERE id = %s; 
        """
        return query

    @property
    def get_new_card_request_info(self):
        query = """
            SELECT r.brand_id, r.category_id, r.type, r.account_id, c.full_name 
            FROM bank.card_requests r
            INNER JOIN bank.accounts a ON r.account_id = a.id
            INNER JOIN bank.clients c ON a.client_id = c.id
            WHERE r.id = %s;
        """
        return query

class TransactionQueries:
    @property
    def create_transaction(self):
        query = """
            INSERT INTO bank.transactions (
                account_id, type, amount, from_to, dt_created
            )
            VALUES (%s, %s, %s, %s, now());
        """
        return query


class PurchaseQueries:
    @property
    def get_card_purchase_request_info(self):
        query = """
                SELECT 
                    c.id,
                    c.card_name, 
                    c.security_code, 
                    c.pin, 
                    c.exp_date, 
                    c.type, 
                    c.active, 
                    c.unlocked, 
                    c.current_limit
                FROM bank.cards c
                WHERE c.card_number = %s;
            """
        return query

    @property
    def get_acc_purchase_request_info(self):
        query = """
            SELECT 
                a.id,
                a.balance
            FROM bank.cards c
            INNER JOIN bank.accounts a ON c.account_id = a.id
            WHERE c.card_number = %s;
        """
        return query

    @property
    def get_statement_purchase_request_info(self):
        query = """
            SELECT 
                i.id,
                i.total
            FROM bank.cards c
            INNER JOIN bank.invoices i ON c.id = i.card_id
            WHERE c.card_number = %s
            AND i.status = 'open';
        """
        return query

    @property
    def create_credit_purchase(self):
        query = """
            INSERT INTO bank.purchases (
                card_id, invoice_id, establishment, location, amount, purchase_status, dt_created
            )
            VALUES (%s, %s, %s, %s, %s, 'confirmed', now());
        """
        return query

    @property
    def create_debit_purchase(self):
        query = """
            INSERT INTO bank.transactions (account_id, card_id, type, amount, from_to, dt_created)
            VALUES (%s, %s, 'purchase', %s, %s, now());
        """
        return query

    @property
    def update_status(self):
        query = """
            UPDATE bank.purchases 
            SET purchase_status = %s
            WHERE id = %s;
        """
        return query


class InvoiceQueries:
    @property
    def create_invoice(self):
        query = """
            INSERT INTO bank.invoices (
                card_id, dt_start, dt_end, dt_due
            )
            VALUES (%s, %s, %s, %s);
        """
        return query

    @property
    def change_status(self):
        query = """
            UPDATE bank.invoices 
            SET status = %s
            WHERE id = %s
            AND card_id = %s;
        """
        return query

    @property
    def pay_statement(self):
        query = """
            UPDATE bank.invoices 
            SET status = 'paid', dt_paid = now()
            WHERE id = %s
            AND card_id = %s;
        """
        return query



