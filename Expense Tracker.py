import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

DATA_FILE = "expense_data.json"
USER_SESSION = {"current_user": None}

# ----------- Data Layer ------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ----------- GUI Layer ------------
class ExpenseTrackerApp:
    def _init_(self, master):
        self.master = master
        self.master.title("Smart Expense Tracker")
        self.master.geometry("700x600")
        self.master.config(bg="#222")

        self.data = load_data()
        self.expenses = []

        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        tk.Label(self.master, text="Enter Username", font=("Arial", 14), bg="#222", fg="white").pack(pady=10)
        self.username_entry = tk.Entry(self.master, font=("Arial", 12))
        self.username_entry.pack(pady=5)

        tk.Button(self.master, text="Login / Register", command=self.login_user,
                  bg="green", fg="white", font=("Arial", 12)).pack(pady=10)

    def login_user(self):
        user = self.username_entry.get().strip()
        if not user:
            messagebox.showerror("Error", "Username cannot be empty.")
            return

        USER_SESSION['current_user'] = user
        if user not in self.data:
            self.data[user] = []

        self.create_main_screen()

    def create_main_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text=f"Welcome, {USER_SESSION['current_user']}", font=("Arial", 16, "bold"),
                 bg="#222", fg="#0f0").pack(pady=10)

        # Income & Expense Inputs
        frame = tk.Frame(self.master, bg="#333")
        frame.pack(pady=10)

        self.amount_entry = tk.Entry(frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Amount ($):", bg="#333", fg="white").grid(row=0, column=0)

        self.category_entry = tk.Entry(frame, width=20)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Category:", bg="#333", fg="white").grid(row=1, column=0)

        self.date_entry = DateEntry(frame, width=17)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(frame, text="Date:", bg="#333", fg="white").grid(row=2, column=0)

        self.type_var = tk.StringVar(value="Expense")
        ttk.Combobox(frame, textvariable=self.type_var, values=["Income", "Expense"], width=17).grid(row=3, column=1, pady=5)
        tk.Label(frame, text="Type:", bg="#333", fg="white").grid(row=3, column=0)

        tk.Button(frame, text="Add Entry", command=self.add_entry, bg="#2196F3", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(self.master, text="Show Charts", command=self.show_charts, bg="#9C27B0", fg="white").pack(pady=10)
        tk.Button(self.master, text="Logout", command=self.create_login_screen, bg="#F44336", fg="white").pack(pady=5)

    def add_entry(self):
        try:
            amt = float(self.amount_entry.get().strip())
            cat = self.category_entry.get().strip()
            date = self.date_entry.get_date().strftime("%Y-%m-%d")
            typ = self.type_var.get()

            if not cat:
                raise ValueError("Category cannot be empty.")

            entry = {"amount": amt, "category": cat, "date": date, "type": typ}
            self.data[USER_SESSION['current_user']].append(entry)
            save_data(self.data)
            messagebox.showinfo("Success", "Entry added successfully!")

            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))

    def show_charts(self):
        entries = self.data.get(USER_SESSION['current_user'], [])
        expenses = {}
        incomes = 0
        total_exp = 0

        for e in entries:
            if e['type'] == 'Expense':
                expenses[e['category']] = expenses.get(e['category'], 0) + e['amount']
                total_exp += e['amount']
            else:
                incomes += e['amount']

        savings = incomes - total_exp
        self.plot_pie_chart(expenses)
        self.plot_bar_chart(incomes, total_exp, savings)

    def plot_pie_chart(self, expenses):
        if not expenses:
            messagebox.showwarning("No Data", "No expenses to plot.")
            return

        plt.figure(figsize=(8, 5))
        plt.title("Expense Distribution")
        plt.pie(expenses.values(), labels=expenses.keys(), autopct="%1.1f%%")
        plt.axis("equal")
        plt.show()

    def plot_bar_chart(self, income, expenses, savings):
        labels = ['Income', 'Expenses', 'Savings']
        values = [income, expenses, savings]
        colors = ['green', 'red', 'blue']

        plt.figure(figsize=(8, 4))
        plt.title("Income vs Expenses vs Savings")
        plt.bar(labels, values, color=colors)
        for i, v in enumerate(values):
            plt.text(i, v + 20, f"${v:.2f}", ha='center', fontweight='bold')
        plt.ylim(0, max(values) + 200)
        plt.show()

# ------------- Run App -------------
if _name_ == "_main_":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()