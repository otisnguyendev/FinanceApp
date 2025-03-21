import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from gui.transaction_form import TransactionForm
from gui.report_viewer import ReportViewer
from gui.wallet_manager import WalletManager
from gui.category_manager import CategoryManager
from gui.chat_form import ChatForm


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

        tk.Label(header_frame, text="Finance Manager", fg="white", bg="#34495E", font=("Poppins", 16, "bold")).pack(
            side="left", padx=20, pady=10)

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
            ("Trợ lý GPT", self.show_chat_gpt)  # Thêm mục mới
        ]
        for text, command in options:
            tk.Button(sidebar_frame, text=text, bg="#2C3E50", fg="white", font=("Poppins", 12, "bold"), bd=0,
                      relief="flat", pady=15, activebackground="#3498DB", activeforeground="white",
                      command=command).pack(fill="x", padx=10, pady=5)

    def create_main_content(self, section_title):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid")
        self.current_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        if section_title == "Trang chủ":
            tk.Label(self.current_frame, text="Quản lý tài chính cá nhân", font=("Poppins", 18, "bold"),
                     bg="#FFFFFF").pack(pady=20)
            tk.Label(self.current_frame,
                     text="Ứng dụng giúp bạn theo dõi chi tiêu, quản lý ví tiền và lập báo cáo tài chính một cách hiệu quả.",
                     font=("Poppins", 12), bg="#FFFFFF", wraplength=800, justify="center").pack(pady=10)

            student_frame = tk.Frame(self.current_frame, bg="#FFFFFF")
            student_frame.pack(pady=10)

            tk.Label(student_frame, text="Sinh viên: Nguyễn Quốc Bảo", font=("Poppins", 12, "bold"),
                     bg="#FFFFFF").pack()
            tk.Label(student_frame, text="Mã số sinh viên: 22140051", font=("Poppins", 12), bg="#FFFFFF").pack()

            tk.Label(student_frame, text="Sinh viên: Mã Kiến Thành", font=("Poppins", 12, "bold"), bg="#FFFFFF").pack(
                pady=5)
            tk.Label(student_frame, text="Mã số sinh viên: 22140026", font=("Poppins", 12), bg="#FFFFFF").pack()

        elif section_title == "Giao dịch":
            TransactionForm(self.current_frame)
        elif section_title == "Danh mục":
            CategoryManager(self.current_frame)
        elif section_title == "Ví tiền":
            WalletManager(self.current_frame)
        elif section_title == "Báo cáo":
            ReportViewer(self.current_frame)
        elif section_title == "Trợ lý GPT":
            self.create_chat_gpt_interface()

    def create_chat_gpt_interface(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = ChatForm(self)
        self.current_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

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

    def show_chat_gpt(self):
        self.create_main_content("Trợ lý GPT")
