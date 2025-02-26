from database.db_connection import get_connection

def add_category(name, type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO categories (name, type) VALUES (?, ?)', (name, type))
    conn.commit()
    conn.close()

def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, type FROM categories')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_category(name, new_name, type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE categories SET name = ?, type = ? WHERE name = ?', (new_name, type, name))
    conn.commit()
    conn.close()

def delete_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
    conn.commit()
    conn.close()