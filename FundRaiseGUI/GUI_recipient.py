import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import messagebox
from FundRaiseLIB.LIB_recipient import RecipientManager
from .GUI_core import MainWindow

class RecipientDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = RecipientManager()  # BLL initialization

        # Track selected fund in "My Funds" table
        self.selected_fund_id = None
        self.my_funds_raw = {}  
        
        tk.Label(self, text="Recipient Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)

        tk.Label(self, text="Create New Fundraising Goal (Funds Needed)",
                 font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        tk.Label(form_frame, text="Service Provider:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.services_data = self.manager.get_services_data()  # LIB call
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
        
        tk.Button(form_frame, text="Submit Fund Request",
                  command=self.create_fund).grid(row=3, columnspan=2, pady=15)

        tk.Label(self, text="Your Existing Funds (Update / Delete)",
                 font=("Arial", 14, "underline")).pack(pady=10)

        crud_frame = tk.Frame(self)
        crud_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ('fund_id', 'service', 'needed', 'raised', 'verified', 'fully_funded')
        self.my_funds_tree = ttk.Treeview(crud_frame, columns=columns, show='headings', height=7)
        for col in columns:
            self.my_funds_tree.heading(col, text=col.capitalize())
            width = 90
            if col == 'service':
                width = 150
            self.my_funds_tree.column(col, anchor=tk.CENTER, width=width)
        self.my_funds_tree.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=5)

        scrollbar = tk.Scrollbar(crud_frame, orient="vertical", command=self.my_funds_tree.yview)
        self.my_funds_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky='ns')

        crud_frame.grid_rowconfigure(0, weight=1)
        crud_frame.grid_columnconfigure(0, weight=1)

        self.my_funds_tree.bind("<<TreeviewSelect>>", self.on_fund_select)

        # Edit fields
        tk.Label(crud_frame, text="Selected Fund ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.selected_fund_label = tk.Label(crud_frame, text="-")
        self.selected_fund_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(crud_frame, text="Amount Needed ($):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.edit_amount_entry = tk.Entry(crud_frame, width=20)
        self.edit_amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Label(crud_frame, text="Proof of Charge (URL):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.edit_proof_entry = tk.Entry(crud_frame, width=40)
        self.edit_proof_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Buttons
        tk.Button(crud_frame, text="Update Selected Fund",
                  command=self.handle_update_fund).grid(
            row=4, column=0, padx=5, pady=10, sticky='e'
        )
        tk.Button(crud_frame, text="Delete Selected Fund",
                  command=self.handle_delete_fund).grid(
            row=4, column=1, padx=5, pady=10, sticky='w'
        )

        # Load data
        self.load_my_funds_table()

    def create_fund(self):
        if not self.user_id:
            messagebox.showerror("Error", "Recipient ID is missing. Please log in again.")
            return

        service_name = self.service_var.get()
        amount_needed_str = self.amount_entry.get()
        proof_of_charge = self.proof_entry.get()

        success, message = self.manager.create_fund(
            self.user_id, service_name, amount_needed_str, proof_of_charge, self.service_map
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.proof_entry.delete(0, tk.END)
            # After creating, refresh table too
            self.load_my_funds_table()
            self.controller.show_frame(MainWindow)
        else:
            messagebox.showerror("Error", message)

    def load_my_funds_table(self):
        """Load all funds created by this recipient."""
        for item in self.my_funds_tree.get_children():
            self.my_funds_tree.delete(item)

        self.my_funds_raw = {}
        self.selected_fund_id = None
        self.selected_fund_label.config(text="-")
        self.edit_amount_entry.delete(0, tk.END)
        self.edit_proof_entry.delete(0, tk.END)

        rows = self.manager.get_recipient_funds(self.user_id)
        for row in rows:
            (fund_id, service_name, amount_needed, amount_raised,
             is_verified, is_fully_funded, proof_of_charge) = row
            self.my_funds_raw[fund_id] = row

            self.my_funds_tree.insert(
                '', tk.END,
                values=(
                    fund_id,
                    service_name,
                    f"{amount_needed:.2f}",
                    f"{amount_raised:.2f}",
                    "YES" if is_verified else "NO",
                    "YES" if is_fully_funded else "NO",
                )
            )

    def on_fund_select(self, event):
        selection = self.my_funds_tree.selection()
        if not selection:
            return
        item_id = selection[0]
        values = self.my_funds_tree.item(item_id, 'values')
        if not values:
            return
        try:
            fund_id = int(values[0])
        except ValueError:
            return

        self.selected_fund_id = fund_id
        self.selected_fund_label.config(text=str(fund_id))

        row = self.my_funds_raw.get(fund_id)
        if row:
            amount_needed = row[2]
            proof = row[6] if row[6] is not None else ""
            self.edit_amount_entry.delete(0, tk.END)
            self.edit_amount_entry.insert(0, str(amount_needed))
            self.edit_proof_entry.delete(0, tk.END)
            self.edit_proof_entry.insert(0, proof)

    def handle_update_fund(self):
        if not self.selected_fund_id:
            messagebox.showerror("Error", "Please select a fund from the table first.")
            return

        amount_str = self.edit_amount_entry.get()
        proof = self.edit_proof_entry.get()

        success, msg = self.manager.update_fund(self.user_id, self.selected_fund_id, amount_str, proof)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_funds_table()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete_fund(self):
        if not self.selected_fund_id:
            messagebox.showerror("Error", "Please select a fund from the table first.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Fund ID {self.selected_fund_id}? "
            f"This will also remove any associated donations."
        ):
            return

        success, msg = self.manager.delete_fund(self.user_id, self.selected_fund_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_funds_table()
        else:
            messagebox.showerror("Error", msg)
