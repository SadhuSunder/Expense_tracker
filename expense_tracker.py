import psycopg2
from psycopg2 import OperationalError
from tkinter import *
from tkinter import messagebox, ttk
from functools import partial


class ExpenseTracker:
    def __init__(self):
        self.db = self.connect_to_db()
        self.cursor = self.db.cursor()
        self.current_user_id = None
        self.login_main_screen()

    
    def connect_to_db(self):
        try:
            return psycopg2.connect(
                host="localhost",
                user="postgres",
                password="root",
                dbname="expense_tracker"
            )
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            exit()

    def login_main_screen(self):
        self.login_screen = Tk()
        self.login_screen.title("Expense Tracker - Login")
        self.login_screen.geometry("460x220")
        self.login_screen.config(bg="white")

        Label(self.login_screen, text="Username: ", font=("consolas", 14, "bold"), bg="white").place(x=20, y=30)
        Label(self.login_screen, text="Password: ", font=("consolas", 14, "bold"), bg="white").place(x=20, y=70)

        self.username_entry = Entry(self.login_screen)
        self.username_entry.place(x=150, y=33)

        self.password_entry = Entry(self.login_screen, show="*")
        self.password_entry.place(x=150, y=73)

        Button(self.login_screen, text="Login", font=("consolas", 12), cursor="hand2", bg="green", fg="white",
               command=self.login).place(x=70, y=120, width=100)
        Button(self.login_screen, text="Register", font=("consolas", 12), cursor="hand2", bg="red", fg="white",
               command=self.register_user).place(x=180, y=120, width=100)

        self.login_screen.mainloop()


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
        
        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()

        if result:
            self.current_user_id = result[0]
            messagebox.showinfo("Login Successful", "Welcome to Expense Tracker!")
            self.login_screen.destroy()
            self.main_main_screen()  
        
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
        
        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.cursor.execute(query, (username, password))
            self.db.commit()
            messagebox.showinfo("Registration Successful", "You can now log in with your credentials.")
        except psycopg2.Error as e:
            messagebox.showerror("Registration Failed", f"Error: {e}")
            self.db.rollback()

    def main_main_screen(self):
        self.main_screen = Tk()
        self.main_screen.title("Expense Tracker")
        self.main_screen.geometry("780x400")
        self.main_screen.config(bg="white")
        self.main_screen.resizable(False, False)

        self.create_expense_form()
        self.create_expense_table()

        self.main_screen.mainloop()

    
    def create_expense_form(self):
        Label(self.main_screen, text="Expense Name: ", font=("Consolas", 12), bg="white").place(x=20, y=20)
        Label(self.main_screen, text="Amount: ", font=("Consolas", 12), bg="white").place(x=240, y=20)
        Label(self.main_screen, text="Date: ", font=("Consolas", 12), bg="white").place(x=400, y=20)

        self.expence_name = Entry(self.main_screen)
        self.expence_name.place(x=20, y=50)

        self.amount = Entry(self.main_screen)
        self.amount.place(x=240, y=50, width=120)

        self.date = Entry(self.main_screen)
        self.date.place(x=400, y=50, width=120)

        Button(self.main_screen, text="Add Expense", font=("Consolas", 10), bg="green", fg="white",
               command=self.add_expense).place(x=550, y=40)
        
        Button(self.main_screen, text="Logout", font=("Consolas", 10), bg="red", fg="white",
                command=self.logout).place(x=20, y=350)
        
        self.show_total_expense()

    
    def create_expense_table(self):
        self.frame = Frame(self.main_screen, bg="white")
        self.frame.place(x=20, y=90, width=740, height=200)

        self.columns = ("id", "name", "amount", "date")

        scroll_x = ttk.Scrollbar(self.frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(self.frame, orient=VERTICAL)

        self.tree = ttk.Treeview(self.frame, columns=self.columns, height= 200, yscrollcommand=scroll_y.set, 
                                 xscrollcommand=scroll_x.set,selectmode="browse")
        
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.tree.xview)
        scroll_y.config(command=self.tree.yview)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Expense Name")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("date", text="Date")

        self.tree['show'] = 'headings'
        self.tree.pack(fill=BOTH, expand=TRUE)

        self.tree.bind('<Double-1>', self.selected)
        self.load_expenses()

    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT id, expense_name, amount, date FROM expenses WHERE user_id = %s"
        self.cursor.execute(query, (self.current_user_id,))
        results = self.cursor.fetchall()
        for expense in results:
            self.tree.insert('', 'end', values=expense)

    def add_expense(self):
        expense_name = self.expence_name.get()
        amount = self.amount.get()
        date = self.date.get()

        if not expense_name or not amount or not date:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        
        try:
            query = "INSERT INTO expenses (user_id, expense_name, amount, date) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (self.current_user_id, expense_name, amount, date))
            self.db.commit()

            messagebox.showinfo("Success", "Expense added successfully.")
            self.load_expenses()
            self.show_total_expense()
            self.clear_expense_form()
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Failed to add expense: {e}")
    
    def add_expense(self):
        expense_name = self.expence_name.get()
        amount = self.amount.get()
        date = self.date.get()

        if not expense_name or not amount or not date:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        
        try:
            query = "INSERT INTO expenses (user_id, expense_name, amount, date) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (self.current_user_id, expense_name, amount, date))
            self.db.commit()

            messagebox.showinfo("Success", "Expense added successfully.")
            self.load_expenses()
            self.show_total_expense()
            self.clear_expense_form()
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Failed to add expense: {e}")

    
    def selected(self, event):
        Button(self.main_screen, text="Update Expense", font=("Consolas", 10), bg="green", fg="white",
               cursor="hand2", command=self.update_expense).place(x=220, y=300)
        
        Button(self.main_screen, text="Delete Expense", font=("Consolas", 10), bg="red", fg="white",
               cursor="hand2", command=self.delete_expense).place(x=90, y=300)
        
    
    def edit_expense_data(self, expense_id):
        try:
            # Create a new popup window
            self.window = Toplevel(self.main_screen)
            self.window.title("Edit Expense")
            self.window.geometry("600x150")
            self.window.config(bg="white")

            # Fetch the expense details from the database
            query = "SELECT * FROM expenses WHERE id = %s"
            self.cursor.execute(query, (expense_id,))
            row = self.cursor.fetchone()

            if row:
                self.get_new_data(row)
            else:
                messagebox.showerror("Error", "Expense not found.")
                self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open edit window: {e}")


    
    def get_new_data(self, row):
        Label(self.window, text="Expense Name", font=("Consolas", 14, "bold"), bg="white").place(x=20,y=20)
        Label(self.window, text="Amount", font=("Consolas", 14, "bold"), bg="white").place(x=240,y=20)
        Label(self.window, text="Date", font=("Consolas", 14, "bold"), bg="white").place(x=400,y=20)

        self.new_expense_name = Entry(self.window)
        self.new_expense_name.insert(END, row[2])
        self.new_expense_name.place(x=20, y=50)

        self.new_amount = Entry(self.window)
        self.new_amount.insert(END, row[3])
        self.new_amount.place(x=240, y=50, width=120)

        self.new_date = Entry(self.window)
        self.new_date.insert(END, row[4])
        self.new_date.place(x=400, y=50, width=120)

        Button(self.window, text="Submit", font=("Consolas", 10), bg="green", fg="white",
               command=partial(self.update_expense, row)).place(x=500, y=40)

    def update_expense(self, row=None):
        if row is None:
            # Called without row (for example, directly from button)
            x = self.tree.selection()
            if not x:
                messagebox.showwarning("Selection Error", "Please select an expense to update.")
                return
            y = self.tree.item(x)['values']
            self.edit_expense_data(y[0])
            return

        if self.new_expense_name.get() == "" or self.new_amount.get() == "" or self.new_date.get() == "":
            messagebox.showerror("Input Error", "Please fill all fields.", parent=self.window)
            return

        try:
            query = """
                UPDATE expenses
                SET expense_name = %s, amount = %s, date = %s
                WHERE id = %s
            """
            self.cursor.execute(query, (
                self.new_expense_name.get(),
                float(self.new_amount.get()),
                self.new_date.get(),
                row[0]
            ))
            self.db.commit()
            messagebox.showinfo("Success", "Expense updated successfully.")
            self.window.destroy()
            self.load_expenses()
            self.show_total_expense()

        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Failed to update expense: {e}")
            self.db.rollback()

    def delete_expense(self):
        x = self.tree.selection()
        y = self.tree.item(x)['values']

        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")

        try:
            if response:
                query = "DELETE FROM expenses WHERE id = %s"
                self.cursor.execute(query, (y[0],))
                self.db.commit()

                messagebox.showinfo("Success", "Expense deleted successfully.")
                self.clear_frame()
                self.create_expense_table()
                self.show_total_expense()
            else:
                messagebox.showinfo("Cancelled", "Expense deletion cancelled.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Failed to delete expense: {e}")

    def show_total_expense(self):
        query = "SELECT SUM(amount) FROM expenses WHERE user_id = %s"
        self.cursor.execute(query, (self.current_user_id,))
        total_expense = self.cursor.fetchone()[0] or 0

        Label(self.main_screen, text=f"Total Expense: ${total_expense}", font=("Consolas", 15), bg="blue", fg="white").place(x=500, y=300)

    
    def clear_screen(self):
        for widget in self.main_screen.winfo_children():
            widget.destroy()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
    
    def clear_expense_form(self):
        self.expence_name.delete(0, END)
        self.amount.delete(0, END)
        self.date.delete(0, END)

    def logout(self):
        self.main_screen.destroy()
        self.current_user_id = None
        self.login_main_screen()


if __name__ == "__main__":
    ExpenseTracker()


        




