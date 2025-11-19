import tkinter as tk
from tkinter import messagebox, ttk
from FundRaiseDAL import DAL_core 
from FundRaiseLIB import LIB_core 

class MainWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        tk.Label(self, text="Fundraising Platform", font=("Arial", 24, "bold")).pack(pady=10)
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Log In", command=lambda: controller.show_frame(LoginWindow), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Register", command=lambda: controller.show_frame(RegistrationWindow), width=15).pack(side=tk.LEFT, padx=10)

        tk.Label(self, text="Active Fundraising Goals", font=("Arial", 16, "underline")).pack(pady=10)
        self.create_funds_table()

        tk.Label(self, text="Latest Donations", font=("Arial", 16, "underline")).pack(pady=10)
        self.create_donations_table()

        self.load_data()

    def create_funds_table(self):
        columns = ('#ID', 'Recipient', 'Service', 'Needed', 'Raised', 'Funded')
        self.funds_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for col in columns:
            self.funds_tree.heading(col, text=col)
            self.funds_tree.column(col, anchor=tk.CENTER, width=70 if col in ('#ID', 'Funded') else 120)
        self.funds_tree.pack(padx=20, pady=5)
        
    def create_donations_table(self):
        columns = ('#D_ID', '#F_ID', 'Donor', 'Amount', 'Date')
        self.donations_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for col in columns:
            self.donations_tree.heading(col, text=col)
            self.donations_tree.column(col, anchor=tk.CENTER, width=70 if col in ('#D_ID', '#F_ID') else 120)
        self.donations_tree.pack(padx=20, pady=5)
        
    def load_data(self):
        # Clear existing data
        for item in self.funds_tree.get_children():
            self.funds_tree.delete(item)
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)

        # Load FundsNeeded - Simple fetch remains in DAL
        funds_data = DAL_core.fetch_funds_data()
        for fund in funds_data:
            needed = f"${fund[3]:.2f}"
            raised = f"${fund[4]:.2f}"
            funded = "YES" if fund[5] else "NO"
            self.funds_tree.insert('', tk.END, values=(fund[0], fund[1], fund[2], needed, raised, funded))

        # Load Donations - Simple fetch remains in DAL
        donations_data = DAL_core.fetch_donations_data()
        for donation in donations_data:
            donor_name = donation[2] if donation[2] is not None else "Anonymous"
            amount = f"${donation[3]:.2f}"
            date_str = donation[4].strftime("%Y-%m-%d") if donation[4] else "N/A"
            self.donations_tree.insert('', tk.END, values=(donation[0], donation[1], donor_name, amount, date_str))

class LoginWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.auth_manager = LIB_core.AuthManager() # Initialize LIB
        tk.Label(self, text="Welcome! Please Log In", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
        tk.Label(self, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(self, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self, text="Login", command=self.handle_login).grid(row=3, column=1, pady=10, sticky='w')
        tk.Button(self, text="Back to Main", command=lambda: controller.show_frame(MainWindow)).grid(row=4, columnspan=2, pady=10)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get() 
        # DELEGATE LOGIN to LIB layer
        user_id, user_role = self.auth_manager.authenticate_user(email, password) 
        
        if user_id:
            # ... success ...
            self.controller.login(user_id, user_role)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            
class RegistrationWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="New User Registration", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
        tk.Label(self, text="Choose Role:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.role_var = tk.StringVar(self)
        self.role_var.set("Recipient")
        roles = ['Recipient', 'Donor', 'Service', 'Admin']
        tk.OptionMenu(self, self.role_var, *roles).grid(row=1, column=1, padx=10, pady=5, sticky='w')
        tk.Button(self, text="Complete Registration", command=self.handle_registration).grid(row=5, column=1, pady=10, sticky='w')
        tk.Button(self, text="Back to Main", command=lambda: controller.show_frame(MainWindow)).grid(row=6, columnspan=2, pady=10)

    def handle_registration(self):
        role = self.role_var.get()
        messagebox.showinfo("Registered", f"Registration simulated! New user created with role: {role}. You can now log in.")
        self.controller.show_frame(LoginWindow)
    pass