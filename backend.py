import csv
import os
from datetime import datetime
import blockchain
import pandas as pd
import matplotlib.pyplot as plt

USERS_FILE = "users.csv"
SETTINGS_FILE = "settings.csv"
CURRENT_USER = None
categories=["Food", "Transport", "Bills", "Entertainment", "Others"]

# -------- USER SESSION --------
def set_current_user(username):
    global CURRENT_USER
    CURRENT_USER = username


def get_filename():
    return f"{CURRENT_USER}_tracker.csv"


# -------- USERS --------
def load_users():
    users = {}

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Username", "Password"])
            writer.writeheader()
        return users

    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row["Username"]] = row["Password"]

    return users


def save_user(username, password):
    file_exists = os.path.exists(USERS_FILE)

    with open(USERS_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Username", "Password"])
        if not file_exists or os.stat(USERS_FILE).st_size == 0:
            writer.writeheader()
        writer.writerow({"Username": username, "Password": password})


# -------- SETTINGS --------
def save_user_settings(username, language, categories, limits):
    file_exists = os.path.exists(SETTINGS_FILE)

    with open(SETTINGS_FILE, "a", newline="") as file:
        fieldnames = ["username", "language", "categories", "limits"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists or os.stat(SETTINGS_FILE).st_size == 0:
            writer.writeheader()

        writer.writerow({
            "username": username,
            "language": language,
            "categories": ",".join(categories),
            "limits": str(limits)
        })


def load_user_settings(username):
    if not os.path.exists(SETTINGS_FILE):
        return None

    with open(SETTINGS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return {
                    "language": row["language"],
                    "categories": row["categories"].split(","),
                    "limits": eval(row["limits"])
                }
    return None


# -------- EXPENSES --------
def load_expenses():
    expenses = []
    filename = get_filename()

    if not os.path.exists(filename):
        return expenses

    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                amount = float(row['amount'])
            except:
                continue

            expenses.append({
                'date': row['date'],
                'time': row['time'],
                'amount': amount,
                'category': row['category'],
                'description': row['description'],
                'txid': row.get('txid', '')
            })

    return expenses


def save_expenses(expenses):
    filename = get_filename()

    if expenses:
        last_expense = expenses[-1]
        try:
            txid = blockchain.store_expense_on_blockchain(last_expense)
            last_expense["txid"] = txid
        except:
            last_expense["txid"] = "Blockchain Error"

    with open(filename, 'w', newline='') as file:
        fieldnames = ['date', 'time', 'amount', 'category', 'description', 'txid']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(expenses)


# -------- DASHBOARD DATA WITH YEAR FILTER --------
# -------- DASHBOARD DATA --------
def get_dashboard_data(username):
    file_name = f"{username}_tracker.csv"

    if not os.path.exists(file_name):
        return None, None

    df = pd.read_csv(file_name)

    if df.empty:
        return None, None

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")

    df['Month'] = df['date'].dt.to_period('M')

    monthly_total = df.groupby('Month')['amount'].sum()

    latest_month = df['Month'].max()
    latest_data = df[df['Month'] == latest_month]
    category_total = latest_data.groupby('category')['amount'].sum()

    return monthly_total, category_total
