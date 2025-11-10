import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
# Import the Data Access Layer for simple fetch calls
from FundRaiseDAL import db_connector 
# Import the NEW Business Logic Layer
from FundRaiseLIB import app_logic

# NOTE: The MainApp class will be passed as 'controller' to handle frame switching.

# --- Public Facing Frames ---

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
        funds_data = db_connector.fetch_funds_data()
        for fund in funds_data:
            needed = f"${fund[3]:.2f}"
            raised = f"${fund[4]:.2f}"
            funded = "YES" if fund[5] else "NO"
            self.funds_tree.insert('', tk.END, values=(fund[0], fund[1], fund[2], needed, raised, funded))

        # Load Donations - Simple fetch remains in DAL
        donations_data = db_connector.fetch_donations_data()
        for donation in donations_data:
            donor_name = donation[2] if donation[2] is not None else "Anonymous"
            amount = f"${donation[3]:.2f}"
            date_str = donation[4].strftime("%Y-%m-%d") if donation[4] else "N/A"
            self.donations_tree.insert('', tk.END, values=(donation[0], donation[1], donor_name, amount, date_str))

class LoginWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.manager = app_logic.FundraisingManager() # Initialize BLL
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
        # DELEGATE LOGIN to BLL
        user_id, user_role = self.manager.authenticate_user(email, password) 

        if user_id:
            messagebox.showinfo("Success", f"Logged in as {user_role}.")
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


# --- Role-Specific Dashboards ---

class AdminDashboard(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.manager = app_logic.FundraisingManager() # Initialize BLL

        tk.Label(self, text="🔑 Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)

        tk.Label(self, text="Funds Verification (Pending Admin Action)", font=("Arial", 14, "underline")).pack(pady=10)

        # Frame for the verification form/list
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # 1. Fund Selection Dropdown
        tk.Label(form_frame, text="Select Fund to Verify:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.funds_data = []
        self.fund_descriptions = []
        self.fund_map = {} 

        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Display Proof of Charge Link (Clickable)
        tk.Label(form_frame, text="Proof for Review:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.proof_label_text = tk.StringVar()
        self.proof_label = tk.Label(form_frame, textvariable=self.proof_label_text, fg='blue', cursor="hand2")
        self.proof_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.proof_label.bind("<Button-1>", self.open_proof_link)

        # 3. Action Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        tk.Button(button_frame, text="✅ Verify Fund", command=self.verify_fund, bg='green', fg='white').pack(side=tk.LEFT, padx=10)
        
        # 4. Bind selection change to update the displayed proof link
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown with unverified funds (Simple fetch from DAL)."""
        self.funds_data = db_connector.fetch_unverified_funds()
        
        self.fund_descriptions = []
        self.fund_map = {}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.funds_data:
            self.fund_var.set("No Pending Funds to Verify")
            self.proof_label_text.set("")
            menu.add_command(label="No Pending Funds to Verify")
            return

        for fund_id, recipient_name, service_name, amount_needed, proof_of_charge in self.funds_data:
            description = f"ID {fund_id} for {recipient_name} (Service: {service_name}, ${amount_needed:.2f})"
            self.fund_descriptions.append(description)
            self.fund_map[description] = (fund_id, proof_of_charge if proof_of_charge else 'N/A')
            
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        self.fund_var.set(self.fund_descriptions[0])
        self.load_current_proof()

    def load_current_proof(self):
        """Loads the proof_of_charge for the currently selected fund into the label."""
        selected_desc = self.fund_var.get()
        if selected_desc in self.fund_map:
            fund_id, current_proof = self.fund_map[selected_desc]
            self.proof_label_text.set(current_proof)
        else:
            self.proof_label_text.set("")
            
    def open_proof_link(self, event):
        """Opens the proof link in the user's default web browser (GUI logic)."""
        link = self.proof_label_text.get()
        if link and link not in ('N/A', 'Loading Funds...', ''):
            try:
                webbrowser.open_new_tab(link)
            except Exception as e:
                messagebox.showerror("Browser Error", f"Could not open link: {link}\nError: {e}")
        elif link == 'N/A':
             messagebox.showinfo("No Proof", "No proof of charge has been provided by the service provider yet.")

    def verify_fund(self):
        """DELEGATE FUND VERIFICATION to BLL."""
        selected_desc = self.fund_var.get()
        
        if selected_desc not in self.fund_map:
            messagebox.showerror("Error", "Please select a valid fund to verify.")
            return

        fund_id, current_proof = self.fund_map[selected_desc]
        
        if current_proof == 'N/A':
            if not messagebox.askyesno("Confirm Verification", "No proof of charge has been provided for this fund. Do you still wish to verify it?"):
                return
        
        # DELEGATE to BLL
        success, message = self.manager.verify_fund(fund_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_funds()
            self.controller.show_frame(MainWindow) 
        else:
            messagebox.showerror("Database Error", message)

class RecipientDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = app_logic.FundraisingManager() # Initialize BLL
        
        tk.Label(self, text="💵 Recipient Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Create New Fundraising Goal (Funds Needed)", font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        tk.Label(form_frame, text="Service Provider:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.services_data = db_connector.fetch_services()
        self.service_names = [name for id, name in self.services_data]
        self.service_map = {name: id for id, name in self.services_data}
        
        self.service_var = tk.StringVar(self)
        if self.service_names:
            self.service_var.set(self.service_names[0])
        else:
            self.service_var.set("No Services Available")

        service_menu = tk.OptionMenu(form_frame, self.service_var, *self.service_names)
        service_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Amount Needed ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Proof of Charge (URL):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.proof_entry = tk.Entry(form_frame, width=20)
        self.proof_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Button(form_frame, text="Submit Fund Request", command=self.create_fund, bg='green', fg='white').grid(row=3, columnspan=2, pady=15)

    def create_fund(self):
        if not self.user_id:
            messagebox.showerror("Error", "Recipient ID is missing. Please log in again.")
            return

        service_name = self.service_var.get()
        amount_needed_str = self.amount_entry.get()
        proof_of_charge = self.proof_entry.get()
        recipient_id = self.user_id

        # DELEGATE FUND CREATION (including validation and DAL transaction) to BLL
        success, message = self.manager.create_fund(
            recipient_id, service_name, amount_needed_str, proof_of_charge, self.service_map
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.proof_entry.delete(0, tk.END)
            self.controller.show_frame(MainWindow)
        else:
            # BLL handles identifying Validation vs. Database errors
            messagebox.showerror("Error", message)

class DonorDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = app_logic.FundraisingManager() # Initialize BLL
        
        tk.Label(self, text="Donor Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Make a New Donation", font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # Fund Selection setup 
        tk.Label(form_frame, text="Select Fund:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.funds_data = []
        self.fund_descriptions = []
        self.fund_id_map = {}
        
        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Active Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Active Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Donation Amount
        tk.Label(form_frame, text="Donation Amount ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Anonymity Option
        tk.Label(form_frame, text="Donate Anonymously:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.is_anonymous_var = tk.BooleanVar(self)
        tk.Checkbutton(form_frame, variable=self.is_anonymous_var).grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Button(form_frame, text="Submit Donation", command=self.submit_donation, bg='blue', fg='white').grid(row=3, columnspan=2, pady=15)
        
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown with active funds (Simple fetch from DAL)."""
        self.funds_data = db_connector.fetch_active_funds()
        self.fund_descriptions = [desc for id, desc, needed, raised, name in self.funds_data]
        self.fund_id_map = {desc: id for id, desc, needed, raised, name in self.funds_data}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.fund_descriptions:
            self.fund_var.set("No Active Funds Available")
            menu.add_command(label="No Active Funds Available")
            return
            
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        self.fund_var.set(self.fund_descriptions[0])

    def submit_donation(self):
        if not self.user_id:
            messagebox.showerror("Error", "Donor ID is missing. Please log in again.")
            return

        fund_description = self.fund_var.get()
        donation_amount_str = self.amount_entry.get()
        is_anonymous = self.is_anonymous_var.get()
        donor_user_id = self.user_id

        # DELEGATE DONATION (including validation and transaction) to BLL
        success, message = self.manager.submit_donation(
            fund_description, donation_amount_str, is_anonymous, self.fund_id_map, donor_user_id
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.is_anonymous_var.set(False)
            self.controller.show_frame(MainWindow) 
        else:
            messagebox.showerror("Error", message)

class ServiceDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = app_logic.FundraisingManager() # Initialize BLL
        
        tk.Label(self, text="Service Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Verify Charge for Funds You Are Providing Service For", font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        tk.Label(form_frame, text="Select Fund to Update:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.funds_data = [] 
        self.fund_descriptions = []
        self.fund_map = {} 
        
        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Proof of Charge (URL):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.proof_entry = tk.Entry(form_frame, width=40)
        self.proof_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Button(form_frame, text="Update Proof of Charge", command=self.update_proof, bg='orange', fg='white').grid(row=2, columnspan=2, pady=15)
        
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown (Simple fetch from DAL)."""
        if not self.user_id:
            return

        self.funds_data = db_connector.fetch_service_funds(self.user_id)
        
        self.fund_descriptions = []
        self.fund_map = {}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.funds_data:
            self.fund_var.set("No Funds Assigned to Your Service")
            self.proof_entry.delete(0, tk.END)
            menu.add_command(label="No Funds Assigned to Your Service")
            return

        for fund_id, recipient_name, amount_needed, proof_of_charge in self.funds_data:
            description = f"Fund ID {fund_id} for {recipient_name} (${amount_needed:.2f})"
            self.fund_descriptions.append(description)
            self.fund_map[description] = (fund_id, proof_of_charge if proof_of_charge else '')
            
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        self.fund_var.set(self.fund_descriptions[0])
        self.load_current_proof()

    def load_current_proof(self):
        """Loads the proof_of_charge for the currently selected fund into the entry field (GUI logic)."""
        selected_desc = self.fund_var.get()
        if selected_desc in self.fund_map:
            fund_id, current_proof = self.fund_map[selected_desc]
            self.proof_entry.delete(0, tk.END)
            self.proof_entry.insert(0, current_proof)
        else:
            self.proof_entry.delete(0, tk.END)

    def update_proof(self):
        """DELEGATE PROOF UPDATE to BLL."""
        selected_desc = self.fund_var.get()
        new_proof = self.proof_entry.get()
        
        if selected_desc not in self.fund_map or not self.user_id:
            messagebox.showerror("Error", "Please select a valid fund.")
            return
        
        # DELEGATE to BLL
        success, message = self.manager.update_fund_proof(selected_desc, new_proof, self.user_id, self.fund_map)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_funds() 
            self.controller.show_frame(MainWindow)
        else:
            messagebox.showerror("Error", message)