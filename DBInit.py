import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    print('\n BOT DB INIT')
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        bees integer NOT NULL
                                        ); """
    sql_create_released_table = """ CREATE TABLE IF NOT EXISTS Released (
                                        id integer PRIMARY KEY,
                                        channel text NOT NULL,
                                        bees integer NOT NULL
                                        ); """

    conn = create_connection("C:\\Users\\Thorn\\Desktop\\BOTS\\Beeees\\DB\\Money.db")
    if conn is not None:
        #create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_released_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
