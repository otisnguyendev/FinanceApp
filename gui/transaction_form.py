import tkinter as tk
from tkinter import ttk, messagebox
from database.transactions import add_transaction
from database.categories import get_categories
from database.wallets import get_wallets

class TransactionForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Thêm giao dịch")
        self.geometry("400x500")
        self.configure(bg="#F5F5F5")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Loại giao dịch:", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        self.type_var = tk.StringVar(value="income")
        tk.Radiobutton(self, text="Thu nhập", variable=self.type_var, value="income", bg="#F5F5F5").pack()
        tk.Radiobutton(self, text="Chi tiêu", variable=self.type_var, value="expense", bg="#F5F5F5").pack()

        tk.Label(self, text="Danh mục:", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        categories = get_categories()
        self.category_var = tk.StringVar()
        category_options = [cat[0] for cat in categories] if categories else ["Chưa có danh mục"]
        self.category_combo = ttk.Combobox(self, textvariable=self.category_var, values=category_options)
        self.category_combo.pack()

        tk.Label(self, text="Số tiền:", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        self.amount_entry = tk.Entry(self)
        self.amount_entry.pack()

        tk.Label(self, text="Ngày (YYYY-MM-DD):", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        self.date_entry = tk.Entry(self)
        self.date_entry.pack()

        tk.Label(self, text="Ghi chú:", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        self.note_entry = tk.Entry(self)
        self.note_entry.pack()

        tk.Label(self, text="Ví tiền:", bg="#F5F5F5", font=("Poppins", 12)).pack(pady=5)
        self.wallet_var = tk.StringVar()
        wallets = get_wallets()
        wallet_options = [f"{w[0]} - {w[1]}" for w in wallets] if wallets else ["Chưa có ví"]
        self.wallet_combo = ttk.Combobox(self, textvariable=self.wallet_var, values=wallet_options)
        self.wallet_combo.pack()

        tk.Button(self, text="Lưu", bg="#2ECC71", fg="white", font=("Poppins", 12, "bold"),
                  command=self.save_transaction).pack(pady=20)

    def save_transaction(self):
        try:
            type = self.type_var.get()
            category = self.category_var.get()
            amount = float(self.amount_entry.get())
            date = self.date_entry.get()
            note = self.note_entry.get()
            wallet_id = int(self.wallet_var.get().split(" - ")[0]) if self.wallet_var.get() else None

            if not all([category, amount, date, wallet_id]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return

            add_transaction(type, category, amount, date, note, wallet_id)
            messagebox.showinfo("Thành công", "Giao dịch đã được thêm!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền phải là một số!")