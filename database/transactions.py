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
    else:
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

def update_transaction(trans_id, type, category, amount, date, note, wallet_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT type, amount, wallet_id FROM transactions WHERE id = ?', (trans_id,))
    old_trans = cursor.fetchone()
    if not old_trans:
        conn.close()
        raise ValueError("Không tìm thấy giao dịch để cập nhật!")
    old_type, old_amount, old_wallet_id = old_trans

    if old_wallet_id == wallet_id:
        if old_type == "income" and type == "income":
            adjustment = amount - old_amount
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (adjustment, wallet_id))
        elif old_type == "expense" and type == "expense":
            adjustment = old_amount - amount
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (adjustment, wallet_id))
        elif old_type == "income" and type == "expense":
            cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (old_amount + amount, wallet_id))
        elif old_type == "expense" and type == "income":
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (old_amount + amount, wallet_id))
    else:
        if old_type == "income":
            cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (old_amount, old_wallet_id))
        else:
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (old_amount, old_wallet_id))
        if type == "income":
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (amount, wallet_id))
        else:
            cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (amount, wallet_id))

    cursor.execute('''
        UPDATE transactions 
        SET type = ?, category = ?, amount = ?, date = ?, note = ?, wallet_id = ?
        WHERE id = ?
    ''', (type, category, amount, date, note, wallet_id, trans_id))

    conn.commit()
    conn.close()

def delete_transaction(trans_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT type, amount, wallet_id FROM transactions WHERE id = ?', (trans_id,))
    trans = cursor.fetchone()
    if not trans:
        conn.close()
        raise ValueError("Không tìm thấy giao dịch để xóa!")
    type, amount, wallet_id = trans

    if type == "income":
        cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (amount, wallet_id))
    else:
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (amount, wallet_id))

    cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
    conn.commit()
    conn.close()