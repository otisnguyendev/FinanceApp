import tkinter as tk
from tkinter import ttk, messagebox

from gui.category_manager import CategoryManager
from gui.transaction_form import TransactionForm
from gui.report_viewer import ReportViewer
from gui.wallet_manager import WalletManager

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản lý tài chính cá nhân")
        self.geometry("1200x700")
        self.configure(bg="#F5F5F5")

        self.create_header()
        self.create_sidebar()
        self.current_frame = None
        self.create_main_content("🏠 Trang chủ")

    def create_header(self):
        header_frame = tk.Frame(self, bg="#34495E", height=60)
        header_frame.pack(side="top", fill="x")

        title_label = tk.Label(header_frame, text="💰 Finance Manager", fg="white", bg="#34495E",
                               font=("Poppins", 16, "bold"))
        title_label.pack(side="left", padx=20, pady=10)

    def create_sidebar(self):
        sidebar_frame = tk.Frame(self, bg="#2C3E50", width=240)
        sidebar_frame.pack(side="left", fill="y")

        options = [
            ("🏠 Trang chủ", self.show_home),
            ("💸 Giao dịch", self.show_transactions),
            ("📂 Danh mục", self.show_categories),
            ("💳 Ví tiền", self.show_wallets),
            ("📊 Báo cáo", self.show_reports),
            ("🎯 Lập kế hoạch", self.show_planning),
            ("⚙ Cài đặt", self.show_settings)
        ]

        for text, command in options:
            btn = tk.Button(sidebar_frame, text=text, bg="#2C3E50", fg="white", font=("Poppins", 12, "bold"), bd=0,
                            relief="flat", pady=15, activebackground="#1ABC9C", activeforeground="white",
                            command=command)
            btn.pack(fill="x", padx=10, pady=5)

    def create_main_content(self, section_title):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self, bg="#FFFFFF")
        self.current_frame.pack(expand=True, fill="both", padx=10, pady=10)

        label = tk.Label(self.current_frame, text=section_title, font=("Poppins", 14, "bold"), fg="#333", bg="#FFFFFF")
        label.pack(pady=20)

        if section_title == "💸 Giao dịch":
            self.create_transaction_buttons()
        elif section_title == "📂 Danh mục":
            self.create_category_buttons()
        elif section_title == "💳 Ví tiền":
            self.create_wallet_buttons()
        elif section_title == "📊 Báo cáo":
            self.create_report_view()
        elif section_title == "🎯 Lập kế hoạch":
            self.create_planning_view()
        elif section_title == "⚙ Cài đặt":
            self.create_settings_view()

    def create_transaction_buttons(self):
        button_frame = tk.Frame(self.current_frame, bg="#FFFFFF")
        button_frame.pack(pady=10)

        add_income_btn = tk.Button(button_frame, text="➕ Thêm thu nhập", bg="#2ECC71", fg="white",
                                   font=("Poppins", 12, "bold"), padx=10, pady=5,
                                   command=lambda: self.open_transaction_form("income"))
        add_expense_btn = tk.Button(button_frame, text="➖ Thêm chi tiêu", bg="#E74C3C", fg="white",
                                    font=("Poppins", 12, "bold"), padx=10, pady=5,
                                    command=lambda: self.open_transaction_form("expense"))
        edit_btn = tk.Button(button_frame, text="✏️ Sửa giao dịch", bg="#F1C40F", fg="white",
                             font=("Poppins", 12, "bold"), padx=10, pady=5)
        delete_btn = tk.Button(button_frame, text="🗑 Xóa giao dịch", bg="#E74C3C", fg="white",
                               font=("Poppins", 12, "bold"), padx=10, pady=5)

        add_income_btn.pack(side="left", padx=10)
        add_expense_btn.pack(side="left", padx=10)
        edit_btn.pack(side="left", padx=10)
        delete_btn.pack(side="left", padx=10)

    def open_transaction_form(self, type):
        form = TransactionForm(self)
        if type == "income":
            form.type_var.set("income")
        else:
            form.type_var.set("expense")

    def create_wallet_buttons(self):
        button_frame = tk.Frame(self.current_frame, bg="#FFFFFF")
        button_frame.pack(pady=10)

        balance_btn = tk.Button(button_frame, text="💰 Quản lý số dư", bg="#2ECC71", fg="white",
                                font=("Poppins", 12, "bold"), padx=10, pady=5)
        add_wallet_btn = tk.Button(button_frame, text="➕ Thêm ví", bg="#3498DB", fg="white",
                                   font=("Poppins", 12, "bold"), padx=10, pady=5)
        transfer_btn = tk.Button(button_frame, text="🔄 Chuyển tiền", bg="#F1C40F", fg="white",
                                 font=("Poppins", 12, "bold"), padx=10, pady=5)

        balance_btn.pack(side="left", padx=10)
        add_wallet_btn.pack(side="left", padx=10)
        transfer_btn.pack(side="left", padx=10)
        WalletManager(self.current_frame)

    def create_category_buttons(self):
        CategoryManager(self.current_frame)

    def create_report_view(self):
        ReportViewer(self.current_frame)

    def create_planning_view(self):
        pass

    def create_settings_view(self):
        pass

    def show_home(self):
        self.create_main_content("🏠 Trang chủ")

    def show_transactions(self):
        self.create_main_content("💸 Giao dịch")

    def show_categories(self):
        self.create_main_content("📂 Danh mục")

    def show_wallets(self):
        self.create_main_content("💳 Ví tiền")

    def show_reports(self):
        self.create_main_content("📊 Báo cáo")

    def show_planning(self):
        self.create_main_content("🎯 Lập kế hoạch")

    def show_settings(self):
        self.create_main_content("⚙ Cài đặt")