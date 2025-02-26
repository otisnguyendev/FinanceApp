import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from database.transactions import get_transactions
from database.db_connection import get_connection

class ReportViewer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Báo cáo giao dịch", font=("Arial", 16, "bold"), fg="#333", bg="#FFFFFF").pack(pady=10)

        filter_frame = tk.Frame(self, bg="#FFFFFF")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Từ ngày (YYYY-MM-DD):", bg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.start_date_entry = tk.Entry(filter_frame, font=("Arial", 12))
        self.start_date_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Đến ngày (YYYY-MM-DD):", bg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=2, padx=5)
        self.end_date_entry = tk.Entry(filter_frame, font=("Arial", 12))
        self.end_date_entry.grid(row=0, column=3, padx=5)

        tk.Button(filter_frame, text="Lọc", bg="#3498DB", fg="white", font=("Arial", 12, "bold"), command=self.apply_filter).grid(row=0, column=4, padx=5)

        columns = ("Loại", "Danh mục", "Số tiền", "Ngày", "Ghi chú", "Ví")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        self.tree.pack(expand=True, fill="both")

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        self.tree.heading("Loại", text="Loại")
        self.tree.heading("Danh mục", text="Danh mục")
        self.tree.heading("Số tiền", text="Số tiền")
        self.tree.heading("Ngày", text="Ngày")
        self.tree.heading("Ghi chú", text="Ghi chú")
        self.tree.heading("Ví", text="Ví")

        self.tree.column("Loại", width=80, anchor="center")
        self.tree.column("Danh mục", width=100, anchor="center")
        self.tree.column("Số tiền", width=100, anchor="center")
        self.tree.column("Ngày", width=100, anchor="center")
        self.tree.column("Ghi chú", width=150, anchor="center")
        self.tree.column("Ví", width=50, anchor="center")

        self.load_data()

    def apply_filter(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        self.load_data(start_date, end_date)
        self.update_chart(start_date, end_date)

    def load_data(self, start_date=None, end_date=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM transactions"
        params = []
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params = [start_date, end_date]
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        conn.close()

        for trans in transactions:
            display_type = "Thu nhập" if trans[1] == "income" else "Chi tiêu"
            self.tree.insert("", "end", values=(display_type, trans[2], trans[3], trans[4], trans[5], trans[6]))

    def update_chart(self, start_date=None, end_date=None):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        conn = get_connection()
        cursor = conn.cursor()

        query_income = "SELECT category, SUM(amount) FROM transactions WHERE type = 'income'"
        query_expense = "SELECT category, SUM(amount) FROM transactions WHERE type = 'expense'"
        params = []
        if start_date and end_date:
            query_income += " AND date BETWEEN ? AND ?"
            query_expense += " AND date BETWEEN ? AND ?"
            params = [start_date, end_date]

        cursor.execute(query_income + " GROUP BY category", params)
        income_data = cursor.fetchall()
        income_categories = [row[0] for row in income_data]
        income_amounts = [row[1] for row in income_data]

        cursor.execute(query_expense + " GROUP BY category", params)
        expense_data = cursor.fetchall()
        expense_categories = [row[0] for row in expense_data]
        expense_amounts = [row[1] for row in expense_data]

        conn.close()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="#F5F5F5")

        if income_categories:
            ax1.pie(income_amounts, labels=income_categories, autopct='%1.1f%%', startangle=90,
                    colors=plt.cm.Pastel1.colors)
            ax1.set_title("Thu nhập theo danh mục", fontsize=12, fontweight="bold", color="#333", fontname="Arial")
        else:
            ax1.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center", fontsize=10, color="#777", fontname="Arial")
            ax1.set_title("Thu nhập theo danh mục", fontsize=12, fontweight="bold", color="#333", fontname="Arial")

        if expense_categories:
            ax2.pie(expense_amounts, labels=expense_categories, autopct='%1.1f%%', startangle=90,
                    colors=plt.cm.Pastel2.colors)
            ax2.set_title("Chi tiêu theo danh mục", fontsize=12, fontweight="bold", color="#333", fontname="Arial")
        else:
            ax2.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center", fontsize=10, color="#777", fontname="Arial")
            ax2.set_title("Chi tiêu theo danh mục", fontsize=12, fontweight="bold", color="#333", fontname="Arial")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(pady=10)