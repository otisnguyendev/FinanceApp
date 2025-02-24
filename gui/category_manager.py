import tkinter as tk
from tkinter import ttk, messagebox
from database.categories import add_category, get_categories

class CategoryManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Quản lý danh mục", font=("Poppins", 14, "bold"), fg="#333", bg="#FFFFFF").pack(pady=10)

        input_frame = tk.Frame(self, bg="#FFFFFF")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Tên danh mục:", bg="#FFFFFF").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Loại:", bg="#FFFFFF").grid(row=1, column=0, padx=5)
        self.type_var = tk.StringVar(value="income")
        ttk.Radiobutton(input_frame, text="Thu nhập", value="income", variable=self.type_var).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(input_frame, text="Chi tiêu", value="expense", variable=self.type_var).grid(row=1, column=1, sticky="e")

        tk.Button(input_frame, text="Thêm danh mục", bg="#2ECC71", fg="white", command=self.add_category).grid(row=2, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Tên", "Loại"), show="headings", height=15)
        self.tree.pack(expand=True, fill="both")

        self.tree.heading("Tên", text="Tên danh mục")
        self.tree.heading("Loại", text="Loại")
        self.tree.column("Tên", width=150)
        self.tree.column("Loại", width=100)

        self.load_categories()

    def load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        categories = get_categories()
        for cat in categories:
            self.tree.insert("", "end", values=cat)

    def add_category(self):
        name = self.name_entry.get()
        type = self.type_var.get()
        try:
            if not name:
                messagebox.showerror("Lỗi", "Tên danh mục không được để trống!")
                return
            add_category(name, type)
            messagebox.showinfo("Thành công", "Danh mục đã được thêm!")
            self.load_categories()
            self.name_entry.delete(0, tk.END)
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Lỗi", "Tên danh mục đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))