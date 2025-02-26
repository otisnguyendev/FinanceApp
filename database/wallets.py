from database.db_connection import get_connection


def add_wallet(name, initial_balance=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO wallets (name, balance) VALUES (?, ?)', (name, initial_balance))
    conn.commit()
    conn.close()


def get_wallets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM wallets')
    rows = cursor.fetchall()
    conn.close()
    return rows


def transfer_money(from_wallet_id, to_wallet_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT balance FROM wallets WHERE id = ?', (from_wallet_id,))
    balance = cursor.fetchone()[0]
    if balance < amount:
        conn.close()
        raise ValueError("Số dư không đủ để chuyển!")

    cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (amount, from_wallet_id))
    cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (amount, to_wallet_id))

    conn.commit()
    conn.close()

def update_wallet(wallet_id, name, balance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE wallets SET name = ?, balance = ? WHERE id = ?', (name, balance, wallet_id))
    conn.commit()
    conn.close()

def delete_wallet(wallet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wallets WHERE id = ?', (wallet_id,))
    conn.commit()
    conn.close()