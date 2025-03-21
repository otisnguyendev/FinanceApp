from datetime import datetime, timedelta
import sqlite3
import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai

API_KEY = "AIzaSyDUCDJ8ZSwU4Di74117qCDphVxpugLb-to"

class ChatForm(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")
        self.parent = parent

        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.create_widgets()

    def create_widgets(self):
        self.chat_text = scrolledtext.ScrolledText(self, wrap="word", font=("Poppins", 12), height=20)
        self.chat_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_text.insert("end", "GPT: Xin chào! Tôi có thể giúp gì cho bạn?\n")
        self.chat_text.config(state="disabled")

        input_frame = tk.Frame(self, bg="#FFFFFF")
        input_frame.pack(fill="x", padx=10, pady=5)

        self.chat_input = tk.Entry(input_frame, font=("Poppins", 12))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.chat_input.bind("<Return>", self.send_message_event)  # Nhấn Enter để gửi

        send_button = tk.Button(input_frame, text="Gửi", font=("Poppins", 12, "bold"),
                                bg="#3498DB", fg="white", command=self.send_message)
        send_button.pack(side="right", padx=5)

    def send_message(self):
        user_message = self.chat_input.get().strip()
        if not user_message:
            return

        self.chat_text.config(state="normal")
        self.chat_text.insert("end", f"Bạn: {user_message}\n")
        self.chat_input.delete(0, "end")

        if "tổng chi tiêu" in user_message.lower():
            gemini_response = self.get_total_expense()
        elif "tổng thu nhập" in user_message.lower():
            gemini_response = self.get_total_income()
        elif "danh sách giao dịch" in user_message.lower():
            gemini_response = self.get_recent_transactions()
        elif "báo cáo chi tiêu tuần" in user_message.lower():
            gemini_response = self.weekly_expense_report()
        else:
            try:
                response = self.model.generate_content(user_message)
                gemini_response = response.text if response.text else "Không có phản hồi."
            except Exception as e:
                gemini_response = f"Lỗi xảy ra: {str(e)}"

        self.chat_text.insert("end", f"GPT: {gemini_response}\n")
        self.chat_text.config(state="disabled")

    def send_message_event(self, event):
        self.send_message()

    def get_total_expense(self):
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
        total_expense = cursor.fetchone()[0] or 0
        conn.close()
        return f"Tổng chi tiêu của bạn là {total_expense:.2f} VND."

    def get_total_income(self):
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
        total_income = cursor.fetchone()[0] or 0
        conn.close()
        return f"Tổng thu nhập của bạn là {total_income:.2f} VND."

    def get_recent_transactions(self):
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, category, amount, type FROM transactions ORDER BY date DESC LIMIT 5")
        transactions = cursor.fetchall()
        conn.close()

        if not transactions:
            return "Không có giao dịch nào."

        response = "🔹 Giao dịch gần đây:\n"
        for date, category, amount, t_type in transactions:
            response += f"📅 {date} | {category} | {'-' if t_type == 'expense' else '+'}{amount:.2f} VND\n"

        return response

    def weekly_expense_report(self):
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        today = datetime.today().date()
        first_day = today.replace(day=1)
        last_day = first_day.replace(month=(today.month % 12) + 1, day=1) - timedelta(days=1)

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income' AND date BETWEEN ? AND ?",
                       (first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND date BETWEEN ? AND ?",
                       (first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")))
        total_month_expense = cursor.fetchone()[0] or 0

        weekly_limit = total_income / 4 if total_income > 0 else total_month_expense / 4
        week_expenses = []
        total_savings_needed = 0

        current_week = (today - first_day).days // 7 + 1
        past_weeks = min(current_week, 4)

        for i in range(past_weeks):
            start_week = first_day + timedelta(days=i * 7)
            end_week = min(start_week + timedelta(days=6), last_day)

            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND date BETWEEN ? AND ?",
                           (start_week.strftime("%Y-%m-%d"), end_week.strftime("%Y-%m-%d")))
            week_total = cursor.fetchone()[0] or 0
            week_expenses.append((start_week.strftime("%d-%m"), end_week.strftime("%d-%m"), week_total))

            if week_total > weekly_limit:
                total_savings_needed += (week_total - weekly_limit)

        conn.close()

        avg_week_expense = sum([w[2] for w in week_expenses]) / past_weeks if past_weeks > 0 else weekly_limit

        response = "**📊 Báo cáo chi tiêu tuần**:\n"
        for i, (start, end, amount) in enumerate(week_expenses):
            percentage = (amount / weekly_limit) * 100 if weekly_limit > 0 else 0

            if percentage <= 80:
                alert = "🟢 Chi tiêu hợp lý"
            elif percentage <= 100:
                alert = "🟡 Cảnh báo nhẹ! Cẩn thận với chi tiêu."
            else:
                alert = "🔴 Cảnh báo cao! Bạn đã vượt mức chi tiêu."

            response += f"🔹 Tuần {i + 1} ({start} - {end}): {amount:.2f} VND ({percentage:.1f}%) - {alert}\n"

        response += "\n📉 **Dự báo chi tiêu các tuần tới**:\n"
        for i in range(past_weeks, 4):
            start_week = first_day + timedelta(days=i * 7)
            end_week = min(start_week + timedelta(days=6), last_day)
            projected_expense = avg_week_expense

            percentage = (projected_expense / weekly_limit) * 100 if weekly_limit > 0 else 0

            if percentage <= 80:
                alert = "🟢 Dự báo tốt"
            elif percentage <= 100:
                alert = "🟡 Cần kiểm soát"
            else:
                alert = "🔴 Cảnh báo cao!"

            response += f"🔹 Tuần {i + 1} ({start_week.strftime('%d-%m')} - {end_week.strftime('%d-%m')}): ~{projected_expense:.2f} VND ({percentage:.1f}%) - {alert}\n"

        if total_savings_needed > 0:
            response += f"\n💰 Bạn cần tiết kiệm lại {total_savings_needed:.2f} VND trong các tuần tới để cân bằng chi tiêu!\n"
        else:
            response += "\n✅ Bạn đang chi tiêu hợp lý! Tiếp tục duy trì thói quen tốt nhé!\n"

        return response




