import tkinter as tk
from tkinter import ttk, messagebox
from database.wallets import add_wallet, get_wallets, transfer_money

class WalletManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Quản lý ví tiền", font=("Poppins", 14, "bold"), fg="#333", bg="#FFFFFF").pack(pady=10)

        input_frame = tk.Frame(self, bg="#FFFFFF")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Tên ví:", bg="#FFFFFF").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Số dư ban đầu:", bg="#FFFFFF").grid(row=1, column=0, padx=5)
        self.balance_entry = tk.Entry(input_frame)
        self.balance_entry.grid(row=1, column=1, padx=5)

        tk.Button(input_frame, text="Thêm ví", bg="#2ECC71", fg="white", command=self.add_wallet).grid(row=2, column=0, columnspan=2, pady=10)

        transfer_frame = tk.Frame(self, bg="#FFFFFF")
        transfer_frame.pack(pady=10)

        tk.Label(transfer_frame, text="Chuyển từ ví:", bg="#FFFFFF").grid(row=0, column=0, padx=5)
        self.from_wallet_var = tk.StringVar()
        self.from_wallet_combo = ttk.Combobox(transfer_frame, textvariable=self.from_wallet_var)
        self.from_wallet_combo.grid(row=0, column=1, padx=5)

        tk.Label(transfer_frame, text="Đến ví:", bg="#FFFFFF").grid(row=1, column=0, padx=5)
        self.to_wallet_var = tk.StringVar()
        self.to_wallet_combo = ttk.Combobox(transfer_frame, textvariable=self.to_wallet_var)
        self.to_wallet_combo.grid(row=1, column=1, padx=5)

        tk.Label(transfer_frame, text="Số tiền:", bg="#FFFFFF").grid(row=2, column=0, padx=5)
        self.transfer_amount_entry = tk.Entry(transfer_frame)
        self.transfer_amount_entry.grid(row=2, column=1, padx=5)

        tk.Button(transfer_frame, text="Chuyển tiền", bg="#F1C40F", fg="white", command=self.transfer_money).grid(row=3, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Tên", "Số dư"), show="headings", height=10)
        self.tree.pack(expand=True, fill="both")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên", text="Tên")
        self.tree.heading("Số dư", text="Số dư")
        self.tree.column("ID", width=50)
        self.tree.column("Tên", width=150)
        self.tree.column("Số dư", width=100)

        self.load_wallets()

    def load_wallets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        wallets = get_wallets()
        wallet_options = [f"{w[0]} - {w[1]}" for w in wallets]
        self.from_wallet_combo['values'] = wallet_options
        self.to_wallet_combo['values'] = wallet_options
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, balance FROM wallets')
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def add_wallet(self):
        name = self.name_entry.get()
        balance = self.balance_entry.get() or "0"
        try:
            balance = float(balance)
            if not name:
                messagebox.showerror("Lỗi", "Tên ví không được để trống!")
                return
            add_wallet(name, balance)
            messagebox.showinfo("Thành công", "Ví đã được thêm!")
            self.load_wallets()
            self.name_entry.delete(0, tk.END)
            self.balance_entry.delete(0, tk.END)
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Lỗi", "Tên ví đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", "Số dư phải là một số!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def transfer_money(self):
        try:
            from_wallet_id = int(self.from_wallet_var.get().split(" - ")[0])
            to_wallet_id = int(self.to_wallet_var.get().split(" - ")[0])
            amount = float(self.transfer_amount_entry.get())

            if from_wallet_id == to_wallet_id:
                messagebox.showerror("Lỗi", "Không thể chuyển tiền cho cùng một ví!")
                return

            transfer_money(from_wallet_id, to_wallet_id, amount)
            messagebox.showinfo("Thành công", "Chuyển tiền thành công!")
            self.load_wallets()
            self.transfer_amount_entry.delete(0, tk.END)
        except ValueError as e:
            if "Số dư không đủ" in str(e):
                messagebox.showerror("Lỗi", "Số dư không đủ để chuyển!")
            else:
                messagebox.showerror("Lỗi", "Số tiền phải là một số!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

from database.db_connection import get_connection  # Import thêm để lấy số dư