import tkinter as tk
from tkinter import messagebox, ttk
from FundRaiseLIB import LIB_donor
from .GUI_core import MainWindow


class DonorDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = LIB_donor.DonorManager()  # LIB initialization

        # Track selected donation in "My Donations"
        self.selected_donation_id = None
        self.my_donations_raw = {}  # donation_id

  
        tk.Label(self, text="Donor Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)

        # Make a New Donation
        tk.Label(self, text="Make a New Donation", font=("Arial", 14, "underline")).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # Fund dropdown
        tk.Label(form_frame, text="Select Fund:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.funds_data = []
        self.fund_descriptions = []
        self.fund_id_map = {}

        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Active Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Active Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Donation amount
        tk.Label(form_frame, text="Donation Amount ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Anonymous checkbox
        tk.Label(form_frame, text="Donate Anonymously:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.is_anonymous_var = tk.BooleanVar(self)
        tk.Checkbutton(form_frame, variable=self.is_anonymous_var).grid(
            row=2, column=1, padx=5, pady=5, sticky='w'
        )

        tk.Button(
            form_frame,
            text="Submit Donation",
            command=self.submit_donation
        ).grid(row=3, columnspan=2, pady=15)

        # Load funds into dropdown
        self.load_funds()


        # My Donations (Read / Update / Delete)
 
        tk.Label(self, text="Your Donations (Update / Delete)",
                 font=("Arial", 14, "underline")).pack(pady=10)

        crud_frame = tk.Frame(self)
        crud_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ('donation_id', 'fund_id', 'amount', 'status', 'date')
        self.my_donations_tree = ttk.Treeview(
            crud_frame, columns=columns, show='headings', height=7
        )
        for col in columns:
            self.my_donations_tree.heading(col, text=col.capitalize())
            width = 90
            if col == 'date':
                width = 130
            self.my_donations_tree.column(col, anchor=tk.CENTER, width=width)

        self.my_donations_tree.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=5)

        scrollbar = tk.Scrollbar(
            crud_frame, orient="vertical", command=self.my_donations_tree.yview
        )
        self.my_donations_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky='ns')

        crud_frame.grid_rowconfigure(0, weight=1)
        crud_frame.grid_columnconfigure(0, weight=1)

        # Bind selection
        self.my_donations_tree.bind("<<TreeviewSelect>>", self.on_donation_select)

        # Edit area
        tk.Label(crud_frame, text="Selected Donation ID:").grid(
            row=1, column=0, padx=5, pady=5, sticky='e'
        )
        self.selected_donation_label = tk.Label(crud_frame, text="-")
        self.selected_donation_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(crud_frame, text="Donation Amount ($):").grid(
            row=2, column=0, padx=5, pady=5, sticky='e'
        )
        self.edit_amount_entry = tk.Entry(crud_frame, width=20)
        self.edit_amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Buttons
        tk.Button(
            crud_frame,
            text="Update Selected Donation",
            command=self.handle_update_donation
        ).grid(row=3, column=0, padx=5, pady=10, sticky='e')

        tk.Button(
            crud_frame,
            text="Delete Selected Donation",
            command=self.handle_delete_donation
        ).grid(row=3, column=1, padx=5, pady=10, sticky='w')

        # Load my donations table
        self.load_my_donations_table()

    # Make a new donation

    def load_funds(self):
        """Fetch and populate active funds in the dropdown using LIB layer."""
        self.funds_data = self.manager.get_active_funds_list()
        self.fund_descriptions = [row[1] for row in self.funds_data]
        self.fund_id_map = {row[1]: row[0] for row in self.funds_data}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.fund_descriptions:
            self.fund_var.set("No Active Funds Available")
            menu.add_command(label="No Active Funds Available")
            return

        for desc in self.fund_descriptions:
            menu.add_command(
                label=desc,
                command=tk._setit(self.fund_var, desc)
            )

        self.fund_var.set(self.fund_descriptions[0])

    def submit_donation(self):
        if not self.user_id:
            messagebox.showerror("Error", "Donor ID is missing. Please log in again.")
            return

        fund_description = self.fund_var.get()
        donation_amount_str = self.amount_entry.get()
        is_anonymous = self.is_anonymous_var.get()

        success, message = self.manager.submit_donation(
            fund_description, donation_amount_str, is_anonymous,
            self.fund_id_map, self.user_id
        )

        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.is_anonymous_var.set(False)
            # refresh "My Donations" table
            self.load_my_donations_table()
            self.controller.show_frame(MainWindow)
        else:
            messagebox.showerror("Error", message)

    def load_my_donations_table(self):
        """Load this donor's donations into the Treeview."""
        for item in self.my_donations_tree.get_children():
            self.my_donations_tree.delete(item)

        self.my_donations_raw = {}
        self.selected_donation_id = None
        self.selected_donation_label.config(text="-")
        self.edit_amount_entry.delete(0, tk.END)

        rows = self.manager.get_my_donations(self.user_id)
        for row in rows:
            donation_id, fund_id, donation_amount, payment_status, donation_date = row
            self.my_donations_raw[donation_id] = row
            date_str = donation_date.strftime("%Y-%m-%d") if donation_date else "N/A"

            self.my_donations_tree.insert(
                '', tk.END,
                values=(
                    donation_id,
                    fund_id,
                    f"{float(donation_amount):.2f}",
                    payment_status,
                    date_str
                )
            )

    def on_donation_select(self, event):
        """When user selects a donation row, load it into edit field."""
        selection = self.my_donations_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        values = self.my_donations_tree.item(item_id, 'values')
        if not values:
            return

        try:
            donation_id = int(values[0])
        except ValueError:
            return

        self.selected_donation_id = donation_id
        self.selected_donation_label.config(text=str(donation_id))

        row = self.my_donations_raw.get(donation_id)
        if row:
            amount = row[2]
            self.edit_amount_entry.delete(0, tk.END)
            self.edit_amount_entry.insert(0, str(amount))

    def handle_update_donation(self):
        """Update selected donation using LIB layer."""
        if not self.selected_donation_id:
            messagebox.showerror("Error", "Please select a donation from the table first.")
            return

        amount_str = self.edit_amount_entry.get()
        success, msg = self.manager.update_donation(
            self.user_id, self.selected_donation_id, amount_str
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_donations_table()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete_donation(self):
        """Delete selected donation using LIB layer."""
        if not self.selected_donation_id:
            messagebox.showerror("Error", "Please select a donation from the table first.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Donation ID {self.selected_donation_id}? "
            f"This may affect the associated fund's raised amount."
        ):
            return

        success, msg = self.manager.delete_donation(self.user_id, self.selected_donation_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_donations_table()
        else:
            messagebox.showerror("Error", msg)
