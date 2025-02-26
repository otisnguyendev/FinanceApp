import tkinter as tk
from tkinter import ttk, messagebox
from database.wallets import add_wallet, get_wallets, transfer_money, update_wallet, delete_wallet
from database.db_connection import get_connection

class WalletManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=20, pady=20)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=("Poppins", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Poppins", 12, "bold"))
        style.configure("TCombobox", font=("Poppins", 12))

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Quản lý ví tiền", font=("Poppins", 16, "bold"), fg="#333", bg="#FFFFFF").grid(row=0, column=0, pady=(0, 20))

        input_frame = tk.Frame(self, bg="#F5F5F5", bd=1, relief="solid")
        input_frame.grid(row=1, column=0, pady=10, sticky="ew", padx=10)
        input_frame.grid_columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Tên ví:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = tk.Entry(input_frame, font=("Poppins", 12), width=25)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(input_frame, text="Số dư ban đầu:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.balance_entry = tk.Entry(input_frame, font=("Poppins", 12), width=25)
        self.balance_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        button_frame_input = tk.Frame(input_frame, bg="#F5F5F5")
        button_frame_input.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(button_frame_input, text="Thêm ví", bg="#2ECC71", fg="white", font=("Poppins", 12, "bold"),
                  command=self.add_wallet, width=15).pack(side="left", padx=5)
        tk.Button(button_frame_input, text="Sửa ví", bg="#F1C40F", fg="white", font=("Poppins", 12, "bold"),
                  command=self.update_wallet, width=15).pack(side="left", padx=5)

        transfer_frame = tk.Frame(self, bg="#F5F5F5", bd=1, relief="solid")
        transfer_frame.grid(row=2, column=0, pady=10, sticky="ew", padx=10)
        transfer_frame.grid_columnconfigure(1, weight=1)

        tk.Label(transfer_frame, text="Chuyển từ ví:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.from_wallet_var = tk.StringVar()
        self.from_wallet_combo = ttk.Combobox(transfer_frame, textvariable=self.from_wallet_var, font=("Poppins", 12), style="TCombobox")
        self.from_wallet_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(transfer_frame, text="Đến ví:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.to_wallet_var = tk.StringVar()
        self.to_wallet_combo = ttk.Combobox(transfer_frame, textvariable=self.to_wallet_var, font=("Poppins", 12), style="TCombobox")
        self.to_wallet_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(transfer_frame, text="Số tiền:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.transfer_amount_entry = tk.Entry(transfer_frame, font=("Poppins", 12), width=25)
        self.transfer_amount_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        tk.Button(transfer_frame, text="Chuyển tiền", bg="#F1C40F", fg="white", font=("Poppins", 12, "bold"),
                  command=self.transfer_money, width=15).grid(row=3, column=0, columnspan=2, pady=10)

        content_frame = tk.Frame(self, bg="#FFFFFF")
        content_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(content_frame, columns=("Tên", "Số dư"), show="headings", style="Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("Tên", text="Tên")
        self.tree.heading("Số dư", text="Số dư")
        self.tree.column("Tên", minwidth=150, width=200, stretch=True, anchor="center")
        self.tree.column("Số dư", minwidth=100, width=150, stretch=True, anchor="center")
        self.tree.bind("<ButtonRelease-1>", self.select_wallet)

        tk.Button(self, text="Xóa ví", bg="#E74C3C", fg="white", font=("Poppins", 12, "bold"),
                  command=self.delete_wallet, width=15).grid(row=4, column=0, pady=10)

        self.load_wallets()

    def load_wallets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, balance FROM wallets')
        wallets = cursor.fetchall()
        conn.close()

        print("Danh sách ví từ database:", wallets)

        if wallets:
            for wallet in wallets:
                self.tree.insert("", "end", values=(wallet[1], wallet[2]))
        else:
            self.tree.insert("", "end", values=("Chưa có ví", ""))

        wallet_options = [w[1] for w in wallets] if wallets else ["Chưa có ví"]
        self.from_wallet_combo['values'] = wallet_options
        self.to_wallet_combo['values'] = wallet_options

    def select_wallet(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[0])  # Tên ví
            self.balance_entry.delete(0, tk.END)
            self.balance_entry.insert(0, values[1])  # Số dư

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

    def update_wallet(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một ví để sửa!")
            return
        old_name = self.tree.item(selected[0])['values'][0]  # Lấy tên ví cũ từ Treeview
        new_name = self.name_entry.get()
        balance = self.balance_entry.get()
        try:
            balance = float(balance)
            if not new_name:
                messagebox.showerror("Lỗi", "Tên ví không được để trống!")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM wallets WHERE name = ?', (old_name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                wallet_id = result[0]
                update_wallet(wallet_id, new_name, balance)
                messagebox.showinfo("Thành công", "Ví đã được cập nhật!")
                self.load_wallets()
                self.name_entry.delete(0, tk.END)
                self.balance_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy ví để cập nhật!")
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Lỗi", "Tên ví đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", "Số dư phải là một số!")

    def delete_wallet(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một ví để xóa!")
            return
        wallet_name = self.tree.item(selected[0])['values'][0]  # Lấy tên ví từ Treeview
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM wallets WHERE name = ?', (wallet_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            wallet_id = result[0]
            if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa ví '{wallet_name}' không?"):
                delete_wallet(wallet_id)
                messagebox.showinfo("Thành công", f"Ví '{wallet_name}' đã được xóa!")
                self.load_wallets()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy ví để xóa!")

    def transfer_money(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM wallets')
            wallets = cursor.fetchall()
            conn.close()

            wallet_dict = {w[1]: w[0] for w in wallets}

            from_wallet_name = self.from_wallet_var.get()
            to_wallet_name = self.to_wallet_var.get()
            from_wallet_id = wallet_dict.get(from_wallet_name)
            to_wallet_id = wallet_dict.get(to_wallet_name)
            amount = float(self.transfer_amount_entry.get())

            if not from_wallet_id or not to_wallet_id:
                messagebox.showerror("Lỗi", "Vui lòng chọn ví hợp lệ!")
                return

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