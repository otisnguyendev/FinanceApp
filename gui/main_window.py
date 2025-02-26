import tkinter as tk
from tkinter import ttk, messagebox
from gui.transaction_form import TransactionForm
from gui.report_viewer import ReportViewer
from gui.wallet_manager import WalletManager
from gui.category_manager import CategoryManager

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản lý tài chính cá nhân")
        self.geometry("1200x800")
        self.configure(bg="#F5F5F5")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_header()
        self.create_sidebar()
        self.current_frame = None
        self.show_home()

    def create_header(self):
        header_frame = tk.Frame(self, bg="#34495E", height=60, bd=1, relief="solid")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_propagate(False)

        tk.Label(header_frame, text="Finance Manager", fg="white", bg="#34495E", font=("Poppins", 16, "bold")).pack(side="left", padx=20, pady=10)

    def create_sidebar(self):
        sidebar_frame = tk.Frame(self, bg="#2C3E50", width=240, bd=1, relief="solid")
        sidebar_frame.grid(row=1, column=0, sticky="ns")
        sidebar_frame.grid_propagate(False)

        options = [
            ("Trang chủ", self.show_home),
            ("Giao dịch", self.show_transactions),
            ("Danh mục", self.show_categories),
            ("Ví tiền", self.show_wallets),
            ("Báo cáo", self.show_reports),
            ("Lập kế hoạch", self.show_planning),
        ]
        for text, command in options:
            tk.Button(sidebar_frame, text=text, bg="#2C3E50", fg="white", font=("Poppins", 12, "bold"), bd=0, relief="flat", pady=15, activebackground="#3498DB", activeforeground="white",
                      command=command).pack(fill="x", padx=10, pady=5)

    def create_main_content(self, section_title):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid")
        self.current_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        if section_title == "Giao dịch":
            TransactionForm(self.current_frame)
        elif section_title == "Danh mục":
            CategoryManager(self.current_frame)
        elif section_title == "Ví tiền":
            WalletManager(self.current_frame)
        elif section_title == "Báo cáo":
            ReportViewer(self.current_frame)
        elif section_title == "Lập kế hoạch":
            pass

    def show_home(self):
        self.create_main_content("Trang chủ")

    def show_transactions(self):
        self.create_main_content("Giao dịch")

    def show_categories(self):
        self.create_main_content("Danh mục")

    def show_wallets(self):
        self.create_main_content("Ví tiền")

    def show_reports(self):
        self.create_main_content("Báo cáo")

    def show_planning(self):
        self.create_main_content("Lập kế hoạch")