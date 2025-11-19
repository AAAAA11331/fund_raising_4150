"""Core GUI frames: MainWindow, LoginWindow, RegistrationWindow."""

import tkinter as tk
from tkinter import messagebox, ttk
from FundRaiseDAL import DAL_core
from FundRaiseLIB import LIB_core


class MainWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Fundraising Platform", font=("Arial", 24, "bold")).pack(pady=10)

        # --- Login/Register Buttons ---
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Log In", command=lambda: controller.show_frame(LoginWindow), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Register", command=lambda: controller.show_frame(RegistrationWindow), width=15).pack(side=tk.LEFT, padx=10)

        # --- Funds Needed Display ---
        tk.Label(self, text="Active Fundraising Goals", font=("Arial", 16, "underline")).pack(pady=10)
        self.create_funds_table()

        # --- Donations Display ---
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
        try:
            funds_data = DAL_core.fetch_funds_data()
        except Exception:
            funds_data = []

        for fund in funds_data:
            needed = f"${fund[3]:.2f}"
            raised = f"${fund[4]:.2f}"
            funded = "YES" if fund[5] else "NO"
            self.funds_tree.insert('', tk.END, values=(fund[0], fund[1], fund[2], needed, raised, funded))

        # Load Donations - Simple fetch remains in DAL
        try:
            donations_data = DAL_core.fetch_donations_data()
        except Exception:
            donations_data = []

        for donation in donations_data:
            donor_name = donation[2] if donation[2] is not None else "Anonymous"
            amount = f"${donation[3]:.2f}"
            date_str = donation[4].strftime("%Y-%m-%d") if donation[4] else "N/A"
            self.donations_tree.insert('', tk.END, values=(donation[0], donation[1], donor_name, amount, date_str))


class LoginWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.auth_manager = LIB_core.AuthManager()  # Initialize LIB

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
            self.controller.login(user_id, user_role)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")


class RegistrationWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="New User Registration", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)

        tk.Label(self, text="Full Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Password:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self, text="Confirm Password:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.confirm_entry = tk.Entry(self, show="*", width=30)
        self.confirm_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="Choose Role:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.role_var = tk.StringVar(self)
        self.role_var.set("Recipient")
        roles = ['Recipient', 'Donor', 'Service', 'Admin']
        role_menu = tk.OptionMenu(self, self.role_var, *roles)
        role_menu.grid(row=5, column=1, padx=10, pady=5, sticky='w')

        # Role-specific fields container (dynamically populated)
        self.role_frame = tk.Frame(self)
        self.role_frame.grid(row=6, column=0, columnspan=2, pady=5, padx=10, sticky='ew')

        # Recipient-specific widgets
        self.recipient_contact_label = tk.Label(self.role_frame, text="Contact Email:")
        self.recipient_contact_entry = tk.Entry(self.role_frame, width=30)

        # Donor-specific widgets
        self.donor_anon_var = tk.BooleanVar(self)
        self.donor_anon_check = tk.Checkbutton(self.role_frame, text="Default to Anonymous Donations", variable=self.donor_anon_var)

        # Service-specific widgets
        self.service_name_label = tk.Label(self.role_frame, text="Service Name:")
        self.service_name_entry = tk.Entry(self.role_frame, width=30)
        self.service_desc_label = tk.Label(self.role_frame, text="Service Description:")
        self.service_desc_entry = tk.Entry(self.role_frame, width=40)
        self.service_tax_label = tk.Label(self.role_frame, text="Tax ID Number:")
        self.service_tax_entry = tk.Entry(self.role_frame, width=30)

        # Initialize role fields and bind role changes
        self.role_var.trace_add('write', lambda *args: self.update_role_fields())
        self.update_role_fields()

        tk.Button(self, text="Complete Registration", command=self.handle_registration).grid(row=7, column=1, pady=10, sticky='w')
        tk.Button(self, text="Back to Main", command=lambda: controller.show_frame(MainWindow)).grid(row=8, columnspan=2, pady=10)

        # LIB auth manager for registration
        self.auth_manager = LIB_core.AuthManager()

    def handle_registration(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_var.get()

        # Collect role-specific data
        role_data = {}
        if role == 'Recipient':
            contact = self.recipient_contact_entry.get().strip() if self.recipient_contact_entry.winfo_ismapped() else ''
            role_data['contact_email'] = contact if contact else email
        elif role == 'Donor':
            role_data['is_anonymous_default'] = bool(self.donor_anon_var.get())
        elif role == 'Service':
            role_data['service_name'] = self.service_name_entry.get().strip()
            role_data['service_description'] = self.service_desc_entry.get().strip()
            role_data['tax_id_number'] = self.service_tax_entry.get().strip()

        if not all([name, email, password, confirm]):
            messagebox.showerror("Registration Error", "All fields are required.")
            return
        if password != confirm:
            messagebox.showerror("Registration Error", "Passwords do not match.")
            return

        # Pass role and role_data tuple to LIB for future handling
        success, result = self.auth_manager.register_user(name, email, password, (role, role_data))
        if success:
            messagebox.showinfo("Registered", f"Successfully registered. Your user id: {result}. You can now log in.")
            self.controller.show_frame(LoginWindow)
        else:
            messagebox.showerror("Registration Failed", result)

    def update_role_fields(self):
        # Clear role_frame children
        for w in self.role_frame.winfo_children():
            w.grid_forget()

        role = self.role_var.get()
        if role == 'Recipient':
            self.recipient_contact_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.recipient_contact_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            if not self.recipient_contact_entry.get():
                self.recipient_contact_entry.insert(0, self.email_entry.get().strip())

        elif role == 'Donor':
            self.donor_anon_check.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=2)

        elif role == 'Service':
            self.service_name_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.service_name_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.service_desc_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
            self.service_desc_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
            self.service_tax_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
            self.service_tax_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)

        # Admin: no extra fields
