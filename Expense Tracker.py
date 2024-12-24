from tkinter import *  
from tkinter import ttk
from matplotlib import pyplot as plt
import mysql.connector
from tkinter import messagebox

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="laptop1234@",
    database="mydb"
)
cur = mydb.cursor()

def add_expense(): 
    
    Date_ = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    monthly_budget = monthly_budget_entry.get()

    if Date_ and category and amount:
        try:
            monthly_budget = float(monthly_budget) if monthly_budget else None
            cur.execute(
                "INSERT INTO expenses (Date_, category, amount, monthly_budget) VALUES (%s, %s, %s, %s)",
                (Date_, category, float(amount), monthly_budget)
            )
            mydb.commit()
            status_label.config(text="Expense added successfully!", fg="green")
            date_entry.delete(0, END)
            category_entry.delete(0, END)

            amount_entry.delete(0, END)
            monthly_budget_entry.delete(0, END)
            view_expenses()
        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")
    else:
        status_label.config(text="Please fill all the fields!", fg="red")
    limit()

def delete_expense():
    cur.execute("delete from expenses")
    mydb.commit()
    view_expenses()


def view_expenses():
    global expenses_tree
    total_expense = 0
    expenses_tree.delete(*expenses_tree.get_children())

    try:
        cur.execute("SELECT * FROM expenses")
        rows = cur.fetchall()
        
        for row in rows:
            Date_, category, amount, monthly_budget = row
            expenses_tree.insert("", END, values=(Date_, category, f"{amount:.2f}", f"{monthly_budget:.2f}" if monthly_budget else ""))
            total_expense += amount

        total_label.config(text=f"Total Expense: {total_expense:.2f}")

       
        expenses_tree.tag_configure('over_budget', background='red')
        expenses_tree.tag_configure('within_budget', background='green')

        for child in expenses_tree.get_children():
            expenses_tree.item(child, tags='')
            amount = float(expenses_tree.item(child, "values")[2])
            monthly_budget = expenses_tree.item(child, "values")[3]
            if monthly_budget:
                if amount > float(monthly_budget):
                    expenses_tree.item(child, tags=('over_budget',))
                else:
                    expenses_tree.item(child, tags=('within_budget',))
            else:
                expenses_tree.item(child, tags='')
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")


def visualize_expense():
    expenses_by_month = {}
    expenses_by_category = {}


    try:
        cur.execute("SELECT * FROM expenses")
        rows = cur.fetchall()

        for row in rows:
            Date_, category, amount, monthly_budget = row
           
            if not isinstance(Date_, str):
                Date_ = Date_.strftime("%Y-%m-%d")
            
            month = Date_.split("-")[1]
            expenses_by_month[month] = expenses_by_month.get(month, 0) + amount
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount

        months = list(expenses_by_month.keys())
        expenses_values = list(expenses_by_month.values())

        plt.figure(figsize=(14, 8))

        plt.subplot(2, 2, 1)
        plt.bar(months, expenses_values, color="skyblue")
        plt.xlabel("Month")
        plt.ylabel("Total Expense")
        plt.title("Expenses by Month")
        plt.xticks(rotation=45)

        
        plt.subplot(2, 2, 2)
        plt.pie(
            list(expenses_by_category.values()),
            labels=list(expenses_by_category.keys()),
            autopct="%1.1f%%",
            colors=plt.cm.tab20.colors,
        )
        plt.title("Expenses by Category")

        plt.tight_layout()
        plt.show()
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def limit():
    cur.execute("SELECT SUM(amount) FROM expenses WHERE DATE_FORMAT(Date_, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    lexpense = cur.fetchone()[0]
    lexpense = float(lexpense) if lexpense else 0.0
    cur.execute("select monthly_budget from expenses where DATE_FORMAT(Date_, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    mbudget = cur.fetchall()

    mbudget = float(mbudget[0][0]) if mbudget else 0.0

    if mbudget:
        limitofex = (lexpense/mbudget)*100
        if(limitofex <= 100):
            messagebox.showwarning("Warning",f"You have used {limitofex}% of your monthly budget !")
        else:
            messagebox.showwarning("Warning","You have exceeded your monthly budget. Tap OK to continue anyway.")

def thismonth():
    cur.execute("select sum(amount) from expenses where DATE_FORMAT(Date_, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    mthex = cur.fetchone()[0]
    messagebox.showwarning("",f"this month {mthex}")

root = Tk()
root.title("Expense Tracker")


date_label = Label(root, text="Date (YYYY-MM-DD):", fg="blue")
date_label.grid(row=0, column=0, padx=5, pady=5)
date_entry = Entry(root)
date_entry.grid(row=0, column=1, padx=5, pady=5)

category_label = Label(root, text="Category:", fg="blue")
category_label.grid(row=1, column=0, padx=5, pady=5)
category_entry = ttk.Combobox(root, values=["Car EMI", "Loan EMI", "Grocery", "Electricity Bill", "Transportation", "Education and Childcare", "Medical Expenses", "Personal Care", "Entertainment", "Rent", "OTT Subscriptions", "Unexpected Expense"], state="readonly")
category_entry.grid(row=1, column=1, padx=5, pady=5)

amount_label = Label(root, text="Amount:", fg="blue")
amount_label.grid(row=2, column=0, padx=5, pady=5)
amount_entry = Entry(root)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

monthly_budget_label = Label(root, text="Monthly Budget:", fg="blue")
monthly_budget_label.grid(row=3, column=0, padx=5, pady=5)
monthly_budget_entry = Entry(root)
monthly_budget_entry.grid(row=3, column=1, padx=5, pady=5)

add_button = Button(root, text="Add Expense", fg="white", bg="black", command=add_expense)
add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

visualize_button = Button(root, text="Visualize Expenses", fg="white", bg="black", command=visualize_expense)
visualize_button.grid(row=8, column=0, columnspan=2, padx=5, pady=10)


columns = ("Date", "Category", "Amount", "Monthly Budget")
expenses_tree = ttk.Treeview(root, columns=columns, show="headings")
expenses_tree.heading("Date", text="Date")


expenses_tree.heading("Category", text="Category")
expenses_tree.heading("Amount", text="Amount")
expenses_tree.heading("Monthly Budget", text="Monthly Budget")
expenses_tree.grid(row=5, column=0, columnspan=3, padx=5, pady=5)


total_label = Label(root, text="")
total_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)


status_label = Label(root, text="", fg="green")
status_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)


view_button = Button(root, text="Reset", fg="white", bg="black", command=delete_expense)
view_button.grid(row=8, column=0, padx=5, pady=10)

delete_button = Button(root, text="This Month", fg="white", bg="black", command=thismonth)
delete_button.grid(row=8, column=1, padx=5, pady=10)

view_expenses()
limit()

root.mainloop()