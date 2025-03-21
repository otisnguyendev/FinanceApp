import tkinter as tk
from tkinter import ttk, messagebox
from database.transactions import add_transaction, get_transactions, update_transaction, delete_transaction, get_expense_summary, detect_outliers, check_spending_alert
from database.categories import get_categories
from database.wallets import get_wallets
from database.db_connection import get_connection

class TransactionForm(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Quản lý giao dịch", bg="#FFFFFF", font=("Poppins", 16, "bold"), fg="#333").pack(pady=(0, 20))

        button_frame = tk.Frame(self, bg="#FFFFFF")
        button_frame.pack(pady=10)

        buttons = [
            ("Thêm thu nhập", "#2ECC71", self.open_add_transaction_form_income),
            ("Thêm chi tiêu", "#E74C3C", self.open_add_transaction_form_expense),
            ("Sửa giao dịch", "#F1C40F", self.edit_transaction),
            ("Xóa giao dịch", "#E74C3C", self.delete_transaction),
            ("Phát hiện bất thường", "#3498DB", self.detect_and_show_outliers)
        ]
        for i, (text, bg, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, bg=bg, fg="white", font=("Poppins", 12, "bold"), padx=10, pady=5,
                            command=command, width=15)
            button_frame.grid_columnconfigure(i, weight=1)
            btn.grid(row=0, column=i, padx=10)

        self.tree = ttk.Treeview(self, columns=("Loại", "Danh mục", "Số tiền", "Ngày", "Ghi chú", "Ví"),
                                 show="headings", style="Treeview")
        self.tree.pack(expand=True, fill="both", pady=10)

        for col in ("Loại", "Danh mục", "Số tiền", "Ngày", "Ghi chú", "Ví"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100, stretch=True)
        self.tree.column("Ghi chú", width=150)

        self.load_transactions()

    def load_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        transactions = get_transactions()
        for trans in transactions:
            wallet_id = trans[6]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM wallets WHERE id = ?', (wallet_id,))
            result = cursor.fetchone()
            wallet_name = result[0] if result else "Không xác định"
            conn.close()
            display_type = "Thu nhập" if trans[1] == "income" else "Chi tiêu"
            self.tree.insert("", "end", iid=trans[0],
                             values=(display_type, trans[2], trans[3], trans[4], trans[5], wallet_name))
        outlier_ids = detect_outliers()
        for trans_id in outlier_ids:
            self.tree.item(trans_id, tags=('outlier',))
        self.tree.tag_configure('outlier', background='#FADBD8')

    def detect_and_show_outliers(self):
        outlier_ids = detect_outliers()
        if not outlier_ids:
            messagebox.showinfo("Kết quả", "Không phát hiện giao dịch bất thường nào!")
            return
        outlier_details = []
        for trans_id in outlier_ids:
            values = self.tree.item(trans_id, 'values')
            if values:
                outlier_details.append(f"ID: {trans_id}, Loại: {values[0]}, Số tiền: {values[2]}, Ngày: {values[3]}")

        messagebox.showwarning("Giao dịch bất thường",
                               "Các giao dịch sau được phát hiện là bất thường:\n\n" + "\n".join(outlier_details))

        for trans_id in outlier_ids:
            self.tree.item(trans_id, tags=('outlier',))
        self.tree.tag_configure('outlier', background='#FADBD8')

    def open_add_transaction_form_income(self):
        self.open_transaction_form("income", "Thêm giao dịch", self.save_transaction)

    def open_add_transaction_form_expense(self):
        self.open_transaction_form("expense", "Thêm giao dịch", self.save_transaction)

    def edit_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một giao dịch để sửa!")
            return

        trans_id = selected[0]
        values = self.tree.item(trans_id, 'values')
        type_value = "income" if values[0] == "Thu nhập" else "expense"
        self.open_transaction_form(type_value, "Sửa giao dịch",
                                   lambda f, t, c, a, d, n, w: self.update_transaction(f, trans_id, t, c, a, d, n, w),
                                   values)

    def open_transaction_form(self, type, title, save_command, values=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("400x500")
        form.configure(bg="#F5F5F5")
        form.transient(self)
        form.grab_set()

        tk.Label(form, text=title, bg="#F5F5F5", font=("Poppins", 16, "bold"), fg="#333").grid(row=0, column=0,
                                                                                              columnspan=2,
                                                                                              pady=(0, 20))

        content_frame = tk.Frame(form, bg="#F5F5F5", bd=1, relief="solid")
        content_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        content_frame.grid_columnconfigure(1, weight=1)

        tk.Label(content_frame, text="Loại giao dịch:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=0, column=0,
                                                                                                 pady=5, sticky="e")
        type_var = tk.StringVar(value=type)
        tk.Radiobutton(content_frame, text="Thu nhập", variable=type_var, value="income", bg="#F5F5F5",
                       font=("Poppins", 12)).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(content_frame, text="Chi tiêu", variable=type_var, value="expense", bg="#F5F5F5",
                       font=("Poppins", 12)).grid(row=1, column=1, sticky="w")

        tk.Label(content_frame, text="Danh mục:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=2, column=0, pady=5,
                                                                                           sticky="e")
        category_var = tk.StringVar(value=values[1] if values else "")
        category_combo = ttk.Combobox(content_frame, textvariable=category_var,
                                      values=[cat[0] for cat in get_categories()] or ["Chưa có danh mục"],
                                      font=("Poppins", 12))
        category_combo.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(content_frame, text="Số tiền:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=3, column=0, pady=5,
                                                                                          sticky="e")
        amount_entry = tk.Entry(content_frame, font=("Poppins", 12), bd=1, relief="solid")
        if values:
            amount_entry.insert(0, values[2])
        amount_entry.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(content_frame, text="Ngày (YYYY-MM-DD):", bg="#F5F5F5", font=("Poppins", 12)).grid(row=4, column=0,
                                                                                                    pady=5, sticky="e")
        date_entry = tk.Entry(content_frame, font=("Poppins", 12), bd=1, relief="solid")
        if values:
            date_entry.insert(0, values[3])
        date_entry.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(content_frame, text="Ghi chú:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=5, column=0, pady=5,
                                                                                          sticky="e")
        note_entry = tk.Entry(content_frame, font=("Poppins", 12), bd=1, relief="solid")
        if values:
            note_entry.insert(0, values[4])
        note_entry.grid(row=5, column=1, pady=5, sticky="ew")

        tk.Label(content_frame, text="Ví tiền:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=6, column=0, pady=5,
                                                                                          sticky="e")
        wallet_var = tk.StringVar(value=values[5] if values and values[5] in [w[1] for w in get_wallets()] else "")
        wallet_combo = ttk.Combobox(content_frame, textvariable=wallet_var,
                                    values=[f"{w[0]} - {w[1]}" for w in get_wallets()] or ["Chưa có ví"],
                                    font=("Poppins", 12))
        wallet_combo.grid(row=6, column=1, pady=5, sticky="ew")

        save_btn = tk.Button(form, text="Lưu", bg="#2ECC71", fg="white", font=("Poppins", 12, "bold"),
                             command=lambda: save_command(form, type_var, category_var, amount_entry, date_entry,
                                                          note_entry, wallet_var),
                             width=15)
        save_btn.grid(row=2, column=0, columnspan=2, pady=20)
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#27AE60"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg="#2ECC71"))

    def check_expense_alert(self):
        current_month_expense, avg_last_3_months = get_expense_summary()
        if avg_last_3_months > 0 and current_month_expense > avg_last_3_months * 1.2:
            messagebox.showwarning("Cảnh báo chi tiêu",
                                   "Chi tiêu tháng này vượt quá 20% so với trung bình 3 tháng trước!")

    def save_transaction(self, form, type_var, category_var, amount_entry, date_entry, note_entry, wallet_var):
        try:
            type = type_var.get()
            category = category_var.get()
            amount = float(amount_entry.get())
            date = date_entry.get()
            note = note_entry.get()
            wallet_id = int(wallet_var.get().split(" - ")[0]) if wallet_var.get() else None

            if not all([category, amount, date, wallet_id]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return

            if type == "expense":
                alert_message = check_spending_alert(wallet_id, amount, date)
                if alert_message:
                    messagebox.showwarning("Cảnh báo chi tiêu", alert_message)

            add_transaction(type, category, amount, date, note, wallet_id)
            messagebox.showinfo("Thành công", "Giao dịch đã được thêm!")
            form.destroy()
            self.load_transactions()
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền phải là một số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def update_transaction(self, form, trans_id, type_var, category_var, amount_entry, date_entry, note_entry,
                           wallet_var):
        try:
            type = type_var.get()
            category = category_var.get()
            amount = float(amount_entry.get())
            date = date_entry.get()
            note = note_entry.get()
            wallet_id = int(wallet_var.get().split(" - ")[0]) if wallet_var.get() else None

            if not all([category, amount, date, wallet_id]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return

            update_transaction(trans_id, type, category, amount, date, note, wallet_id)
            messagebox.showinfo("Thành công", "Giao dịch đã được cập nhật!")
            form.destroy()
            self.load_transactions()
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền phải là một số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một giao dịch để xóa!")
            return

        trans_id = selected[0]
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa giao dịch này không?"):
            delete_transaction(trans_id)
            messagebox.showinfo("Thành công", "Giao dịch đã được xóa!")
            self.load_transactions()