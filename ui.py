import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import backend
import new_chart

# ================= LOGIN PAGE =================
class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("SpendWise Login")
        self.root.geometry("350x250")

        tk.Label(root, text="SpendWise Login",
                 font=("Arial", 18, "bold")).pack(pady=15)

        tk.Label(root, text="Username").pack()
        self.username = tk.Entry(root)
        self.username.pack()

        tk.Label(root, text="Password").pack()
        self.password = tk.Entry(root, show="*")
        self.password.pack()

        tk.Button(root, text="Login", width=15,
                  command=self.login).pack(pady=10)
        tk.Button(root, text="Register", width=15,
                  command=self.register).pack()

    def login(self):
        users = backend.load_users()
        username = self.username.get().strip()
        password = self.password.get().strip()

    # CHECK CREDENTIALS FIRST
        if username in users and users[username] == password:
            backend.set_current_user(username)
            settings = backend.load_user_settings(username)

            self.root.destroy()
            main_root = tk.Tk()

        # first time user → open setup
            if settings is None:
               SetupPage(main_root)
            else:
               ExpensePage(main_root)

            main_root.mainloop()

        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        users = backend.load_users()
        username = self.username.get().strip()
        password = self.password.get().strip()

        if username in users:
            messagebox.showerror("Error", "User exists")
            return

        backend.save_user(username, password)
        messagebox.showinfo("Success", "Registered!")


# ================= EXPENSE TRACKER =================
class ExpensePage:
    def __init__(self, root):
        self.root = root
        self.root.title("SpendWise Expense Tracker")
        self.root.geometry("900x600")

        self.expenses = backend.load_expenses()

        self.setup_ui()
        self.refresh_table()

        # draw chart initially
        import new_chart
        new_chart.draw_charts(self.chart_frame, self.expenses)

    def setup_ui(self):
        # FORM
        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Amount").grid(row=0, column=0)
        self.amount = tk.Entry(form)
        self.amount.grid(row=0, column=1)

        tk.Label(form, text="Category").grid(row=0, column=2)
        self.category = ttk.Combobox(form, values=backend.categories)
        self.category.grid(row=0, column=3)

        tk.Label(form, text="Description").grid(row=0, column=4)
        self.desc = tk.Entry(form)
        self.desc.grid(row=0, column=5)

        tk.Button(form, text="Add Expense",
                  command=self.add_expense).grid(row=0, column=6, padx=10)

        # TABLE
        self.tree = ttk.Treeview(
            self.root,
            columns=("Date","Time","Amount","Category","Description","TXID"),
            show="headings"
        )

        for col in ("Date","Time","Amount","Category","Description","TXID"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True)

        # CHART AREA
        self.chart_frame = tk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True)

    def add_expense(self):
        expense = {
            "date": datetime.now().strftime("%d-%m-%Y"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "amount": float(self.amount.get()),
            "category": self.category.get(),
            "description": self.desc.get()
        }

        self.expenses.append(expense)
        backend.save_expenses(self.expenses)

        self.refresh_table()

        # refresh charts after adding expense
        import new_chart
        new_chart.draw_charts(self.chart_frame, self.expenses)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        self.expenses = backend.load_expenses()

        for e in self.expenses:
            self.tree.insert("", "end", values=(
                e["date"],
                e["time"],
                e["amount"],
                e["category"],
                e["description"],
                e.get("txid","")
            ))

# ================= SETUP PAGE =================
class SetupPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Initial Setup")
        self.root.geometry("400x500")

        tk.Label(root, text="Select Language",
                 font=("Arial", 14, "bold")).pack(pady=10)

        self.language = tk.StringVar(value="English")

        ttk.Combobox(root,
                     textvariable=self.language,
                     values=["English"]).pack()

        tk.Label(root, text="Select Categories (min 1)",
                 font=("Arial", 14, "bold")).pack(pady=10)

        self.categories = {
            "Bills": tk.BooleanVar(),
            "Fees": tk.BooleanVar(),
            "Grocery and Provisions": tk.BooleanVar(),
            "Insurance": tk.BooleanVar(),
            "Monthly Subscription": tk.BooleanVar(),
            "Monthly Transfers": tk.BooleanVar(),
            "Rent": tk.BooleanVar(),
            "Restaurant Expenses": tk.BooleanVar(),
            "Tax": tk.BooleanVar(),
            "Travel Expenses": tk.BooleanVar(),
            "Miscellaneous": tk.BooleanVar(),
            "Other": tk.BooleanVar(),
        }

        for cat, var in self.categories.items():
            tk.Checkbutton(root, text=cat,
                           variable=var).pack(anchor="w")

        tk.Button(root, text="Next",
                  command=self.generate_limits).pack(pady=10)

    def generate_limits(self):

        selected = [c for c, v in self.categories.items() if v.get()]

        if not selected:
            messagebox.showerror("Error", "Select at least 1 category")
            return

        self.limit_entries = {}

        tk.Label(self.root, text="Set Monthly Limits",
                 font=("Arial", 14, "bold")).pack(pady=10)

        for cat in selected:
            tk.Label(self.root, text=f"{cat} Limit").pack()
            entry = tk.Entry(self.root)
            entry.pack()
            self.limit_entries[cat] = entry

        tk.Button(self.root, text="Save Setup",
                  command=self.save_setup).pack(pady=15)

    def save_setup(self):

        limits = {}

        for cat, entry in self.limit_entries.items():
            try:
                limits[cat] = float(entry.get())
            except:
                messagebox.showerror("Error",
                                     f"Enter valid limit for {cat}")
                return

        backend.save_user_settings(
            backend.CURRENT_USER,
            self.language.get(),
            list(self.limit_entries.keys()),
            limits
        )


        messagebox.showinfo("Success", "Setup Completed")

        self.root.destroy()
        main_root = tk.Tk()
        ExpensePage(main_root)
        main_root.mainloop()