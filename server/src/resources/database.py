import psycopg2.extras
import os

#DB_HOST = os.environ.get("PG_DB_HOST")
#DB_USER = os.environ.get("PG_DB_USER")
#DB_PWD = os.environ.get("PG_DB_PWD")
#DB_NAME = os.environ.get("PG_DB_NAME")

DB_HOST = "127.0.0.1"
DB_USER = "postgres"
DB_PWD = "postgres"
DB_NAME = "bank"

def connect_to_database():
    conn_object = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PWD,
        dbname=DB_NAME,
        port=5435
    )
    return conn_object


if __name__ == "__main__":
    with connect_to_database() as conn:
        cur = conn.cursor()
        cur.execute("select * from bank.clients")
        print(cur.rowcount)
        res = list(cur.fetchall()[0])
        print(res)
    cur.close()
    conn.close()
