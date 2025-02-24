from database.db_connection import get_connection


def add_transaction(type, category, amount, date, note, wallet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (type, category, amount, date, note, wallet_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (type, category, amount, date, note, wallet_id))

    if type == 'income':
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (amount, wallet_id))
    else:  # expense
        cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (amount, wallet_id))

    conn.commit()
    conn.close()


def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    rows = cursor.fetchall()
    conn.close()
    return rows