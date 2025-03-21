from database.db_connection import get_connection
from datetime import datetime, timedelta
import numpy as np

def add_transaction(type, category, amount, date, note, wallet_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (type, category, amount, date, note, wallet_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (type, category, amount, date, note, wallet_id))

        balance_update = amount if type == 'income' else -amount
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (balance_update, wallet_id))
        conn.commit()

def get_transactions():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
        return cursor.fetchall()

def update_transaction(trans_id, type, category, amount, date, note, wallet_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT type, amount, wallet_id FROM transactions WHERE id = ?', (trans_id,))
        old_trans = cursor.fetchone()
        if not old_trans:
            raise ValueError("Không tìm thấy giao dịch để cập nhật!")

        old_type, old_amount, old_wallet_id = old_trans
        old_balance_update = old_amount if old_type == 'income' else -old_amount
        new_balance_update = amount if type == 'income' else -amount

        if old_wallet_id != wallet_id:
            cursor.execute('UPDATE wallets SET balance = balance - ? WHERE id = ?', (old_balance_update, old_wallet_id))
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (new_balance_update, wallet_id))
        else:
            balance_adjustment = new_balance_update - old_balance_update
            cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (balance_adjustment, wallet_id))

        cursor.execute('''
            UPDATE transactions 
            SET type = ?, category = ?, amount = ?, date = ?, note = ?, wallet_id = ?
            WHERE id = ?
        ''', (type, category, amount, date, note, wallet_id, trans_id))
        conn.commit()

def delete_transaction(trans_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT type, amount, wallet_id FROM transactions WHERE id = ?', (trans_id,))
        trans = cursor.fetchone()
        if not trans:
            raise ValueError("Không tìm thấy giao dịch để xóa!")

        type, amount, wallet_id = trans
        balance_update = -amount if type == 'income' else amount
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE id = ?', (balance_update, wallet_id))
        cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
        conn.commit()

def get_expense_summary():
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    three_months_ago = first_day_of_month - timedelta(days=90)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'expense' AND date >= ?
        ''', (first_day_of_month,))
        current_month_expense = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT SUM(amount) / 3 FROM transactions
            WHERE type = 'expense' AND date >= ? AND date < ?
        ''', (three_months_ago, first_day_of_month))
        avg_last_3_months = cursor.fetchone()[0] or 0

    return current_month_expense, avg_last_3_months

def detect_outliers():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount FROM transactions WHERE type = 'expense'")
        transactions = cursor.fetchall()

    if not transactions:
        return []

    ids, amounts = zip(*transactions)
    amounts = np.array(amounts)
    mean, std_dev = np.mean(amounts), np.std(amounts)
    z_scores = np.abs((amounts - mean) / std_dev) if std_dev > 0 else np.zeros_like(amounts)
    Q1, Q3 = np.percentile(amounts, [25, 75])
    IQR = Q3 - Q1
    lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

    return [ids[i] for i, amount in enumerate(amounts) if z_scores[i] > 3 or amount < lower_bound or amount > upper_bound]

def get_monthly_income(wallet_id, year, month):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) 
            FROM transactions 
            WHERE type = 'income' 
            AND wallet_id = ? 
            AND strftime('%Y-%m', date) = ?
        """, (wallet_id, f"{year}-{month:02d}"))
        result = cursor.fetchone()[0]
        return result if result else 0

def get_weekly_expenses(wallet_id, year, month, week_start, week_end):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) 
            FROM transactions 
            WHERE type = 'expense' 
            AND wallet_id = ? 
            AND date BETWEEN ? AND ?
        """, (wallet_id, f"{year}-{month:02d}-{week_start:02d}", f"{year}-{month:02d}-{week_end:02d}"))
        result = cursor.fetchone()[0]
        return result if result else 0

def predict_spending_limit(wallet_id, year, month):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', date), SUM(amount) 
            FROM transactions 
            WHERE type = 'expense' AND wallet_id = ? 
            GROUP BY strftime('%Y-%m', date)
            HAVING strftime('%Y-%m', date) < ?
        """, (wallet_id, f"{year}-{month:02d}"))
        past_expenses = cursor.fetchall()

    if not past_expenses:
        return None

    amounts = [expense[1] for expense in past_expenses]
    return np.mean(amounts)

def check_spending_alert(wallet_id, amount, date):
    dt = datetime.strptime(date, "%Y-%m-%d")
    year, month, day = dt.year, dt.month, dt.day

    week = (day - 1) // 7 + 1
    week_start, week_end = (week - 1) * 7 + 1, min(week * 7, 28)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'expense' AND wallet_id = ? AND date BETWEEN ? AND ?
        ''', (wallet_id, f"{year}-{month:02d}-{week_start:02d}", f"{year}-{month:02d}-{week_end:02d}"))
        current_week_expenses = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT AVG(amount) FROM (
                SELECT SUM(amount) as amount FROM transactions
                WHERE type = 'expense' AND wallet_id = ?
                GROUP BY strftime('%Y-%m', date)
                HAVING strftime('%Y-%m', date) < ?
            )
        ''', (wallet_id, f"{year}-{month:02d}"))
        predicted_limit = cursor.fetchone()[0] or 0

    weekly_limit = predicted_limit / 4
    total_weekly_expenses = current_week_expenses + amount

    if total_weekly_expenses > weekly_limit:
        return f"Cảnh báo: Chi tiêu tuần {week} vượt mức dự đoán ({total_weekly_expenses:,.0f}/{weekly_limit:,.0f} VND)!"
    return None
