from gui import FinanceApp
from database.db_connection import init_db

if __name__ == "__main__":
    init_db()
    app = FinanceApp()
    app.mainloop()