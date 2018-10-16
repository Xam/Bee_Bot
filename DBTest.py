import sqlite3
from sqlite3 import Error

DB = "C:\\Users\\Thorn\\Desktop\\BOTS\\Beeees\\DB\\Money.db"


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def create_user(conn, users):
    sql = ''' INSERT INTO users(name,bees)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, users)
    return cur.lastrowid


def select_user_by_id(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    rows = cur.fetchall()
    for row in rows:
        print(row)


def select_user_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    rows = cur.fetchall()
    for row in rows:
        print(row)


def select_all_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    for row in rows:
        print(row)


def update_user_by_id(conn, users):
    sql = ''' UPDATE users
              SET bees = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def update_user_by_name(conn, users):
    sql = ''' UPDATE users
              SET bees = ? 
              WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def delete_user_by_id(conn, id):
    sql = 'DELETE FROM users WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))


def delete_user_by_name(conn, name):
    sql = 'DELETE FROM users WHERE name=?'
    cur = conn.cursor()
    cur.execute(sql, (name,))


def delete_all_users(conn):
    sql = 'DELETE FROM users'
    cur = conn.cursor()
    cur.execute(sql)


def get_bees(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    bees = cur.fetchone()
    return bees[2]


def add_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    total = cur_bees + bees
    args = (total, name)
    update_user_by_name(conn, args)


def sub_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    total = cur_bees - bees
    if total <= 0:
        total = 0
    args = (total, name)
    update_user_by_name(conn, args)


def flarm():
    conno = create_connection(DB)
    if conno is not None:
        with conno:
            print('\n--Printing all rows...')
            select_all_users(conno)

            print('\n--Adding 7 bees to current...')
            add_bees(conno, 'Shade', 7)

            print('\n--Selecting by name...')
            select_user_by_name(conno, 'Shade')

            print('\n--Printing all rows...')
            select_all_users(conno)
    else:
        print("Error! cannot create the database connection.")


def main():
    print('\n BOT DB TEST -- No Discord Connection')
    conn = create_connection(DB)
    if conn is not None:
        with conn:
            print('\nClearing DB')
            delete_all_users(conn)

            print('\nCreating User...')
            user_thorn = ('Thorn', 7)
            create_user(conn, user_thorn)
            user_shade = ('Shade', 17)
            create_user(conn, user_shade)
            user_nik = ('Nik', 18)
            create_user(conn, user_nik)

            print('\nPrinting all rows...')
            select_all_users(conn)

            print('\nUpdating overall bees for Shade...')
            user_shade_bees = (50, 'Shade')
            update_user_by_name(conn, user_shade_bees)

            print('Adding 7 bees to current...')
            add_bees(conn, 'Shade', 7)

            print('\nSelecting by name...')
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('Subbing 9 bees to current...')
            sub_bees(conn, 'Shade', 9)
            select_user_by_name(conn, 'Shade')

            print('\nPrinting all rows...')
            select_all_users(conn)
    else:
        print("Error! cannot create the database connection.")

    #flarm()


if __name__ == '__main__':
    main()
