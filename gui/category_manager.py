import tkinter as tk
from tkinter import ttk, messagebox
from database.categories import add_category, get_categories, update_category, delete_category

class CategoryManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.pack(expand=True, fill="both", padx=20, pady=20)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=("Poppins", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Poppins", 12, "bold"))
        style.configure("TRadiobutton", font=("Poppins", 12), background="#F5F5F5")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Quản lý danh mục", font=("Poppins", 16, "bold"), fg="#333", bg="#FFFFFF").grid(row=0, column=0, pady=(0, 20))

        input_frame = tk.Frame(self, bg="#F5F5F5", bd=1, relief="solid")
        input_frame.grid(row=1, column=0, pady=10, sticky="ew", padx=10)
        input_frame.grid_columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Tên danh mục:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = tk.Entry(input_frame, font=("Poppins", 12), width=25)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(input_frame, text="Loại:", bg="#F5F5F5", font=("Poppins", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.type_var = tk.StringVar(value="income")
        ttk.Radiobutton(input_frame, text="Thu nhập", value="income", variable=self.type_var, style="TRadiobutton").grid(row=1, column=1, padx=5, pady=(5, 2), sticky="w")
        ttk.Radiobutton(input_frame, text="Chi tiêu", value="expense", variable=self.type_var, style="TRadiobutton").grid(row=2, column=1, padx=5, pady=(2, 5), sticky="w")

        content_frame = tk.Frame(self, bg="#FFFFFF")
        content_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(content_frame, bg="#FFFFFF")
        button_frame.grid(row=0, column=0, pady=10, sticky="ew")
        tk.Button(button_frame, text="Thêm danh mục", bg="#2ECC71", fg="white", font=("Poppins", 12, "bold"),
                  command=self.add_category, width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Sửa danh mục", bg="#F1C40F", fg="white", font=("Poppins", 12, "bold"),
                  command=self.update_category, width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Xóa danh mục", bg="#E74C3C", fg="white", font=("Poppins", 12, "bold"),
                  command=self.delete_category, width=15).pack(side="left", padx=5)

        self.tree = ttk.Treeview(content_frame, columns=("Tên", "Loại"), show="headings", style="Treeview")
        self.tree.grid(row=1, column=0, sticky="nsew")

        self.tree.heading("Tên", text="Tên danh mục")
        self.tree.heading("Loại", text="Loại")
        self.tree.column("Tên", minwidth=150, width=200, stretch=True, anchor="center")
        self.tree.column("Loại", minwidth=100, width=150, stretch=True, anchor="center")
        self.tree.bind("<ButtonRelease-1>", self.select_category)

        self.load_categories()

    def load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        categories = get_categories()
        for cat in categories:
            name, type_ = cat
            display_type = "Thu nhập" if type_ == "income" else "Chi tiêu"
            self.tree.insert("", "end", values=(name, display_type))

    def select_category(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[0])
            self.type_var.set("income" if values[1] == "Thu nhập" else "expense")

    def add_category(self):
        name = self.name_entry.get()
        type_ = self.type_var.get()
        try:
            if not name:
                messagebox.showerror("Lỗi", "Tên danh mục không được để trống!")
                return
            add_category(name, type_)
            messagebox.showinfo("Thành công", "Danh mục đã được thêm!")
            self.load_categories()
            self.name_entry.delete(0, tk.END)
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Lỗi", "Tên danh mục đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", str(e))

    def update_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một danh mục để sửa!")
            return
        old_name = self.tree.item(selected[0])['values'][0]
        new_name = self.name_entry.get()
        type_ = self.type_var.get()
        try:
            if not new_name:
                messagebox.showerror("Lỗi", "Tên danh mục không được để trống!")
                return
            update_category(old_name, new_name, type_)
            messagebox.showinfo("Thành công", "Danh mục đã được cập nhật!")
            self.load_categories()
            self.name_entry.delete(0, tk.END)
        except ValueError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Lỗi", "Tên danh mục đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", str(e))

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn một danh mục để xóa!")
            return
        name = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa danh mục '{name}' không?"):
            delete_category(name)
            messagebox.showinfo("Thành công", f"Danh mục '{name}' đã được xóa!")
            self.load_categories()