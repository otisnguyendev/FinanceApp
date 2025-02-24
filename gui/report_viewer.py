import tkinter as tk
from tkinter import ttk
from database.transactions import get_transactions

class ReportViewer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Báo cáo giao dịch", font=("Poppins", 14, "bold"), fg="#333", bg="#FFFFFF").pack(pady=10)

        columns = ("ID", "Loại", "Danh mục", "Số tiền", "Ngày", "Ghi chú", "Ví")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.pack(expand=True, fill="both")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Loại", text="Loại")
        self.tree.heading("Danh mục", text="Danh mục")
        self.tree.heading("Số tiền", text="Số tiền")
        self.tree.heading("Ngày", text="Ngày")
        self.tree.heading("Ghi chú", text="Ghi chú")
        self.tree.heading("Ví", text="Ví")

        self.tree.column("ID", width=50)
        self.tree.column("Loại", width=80)
        self.tree.column("Danh mục", width=100)
        self.tree.column("Số tiền", width=100)
        self.tree.column("Ngày", width=100)
        self.tree.column("Ghi chú", width=150)
        self.tree.column("Ví", width=50)

        self.load_data()

    def load_data(self):
        transactions = get_transactions()
        for trans in transactions:
            self.tree.insert("", "end", values=trans)