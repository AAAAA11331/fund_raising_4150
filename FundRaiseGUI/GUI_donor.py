import tkinter as tk
from tkinter import messagebox, ttk
from FundRaiseLIB import LIB_donor


class DonorDashboard(tk.Frame):
    """Donor-facing dashboard: submit donations and manage own donations."""

    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = LIB_donor.DonorManager()

        self.selected_donation_id = None
        self.my_donations_raw = {}

        tk.Label(self, text="Donor Dashboard", font=("Arial", 18, "bold")).pack(pady=8)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Edit Profile", command=lambda: controller.open_profile()).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Logout", command=controller.logout).pack(side=tk.LEFT, padx=6)

        # New donation form
        tk.Label(self, text="Make a New Donation", font=("Arial", 14, "underline")).pack(pady=6)
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=6, fill='x')

        tk.Label(form_frame, text="Select Fund:").grid(row=0, column=0, sticky='w')
        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Active Funds...")
        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, "Loading Active Funds...")
        self.fund_menu.grid(row=0, column=1, sticky='ew')

        tk.Label(form_frame, text="Donation Amount ($):").grid(row=1, column=0, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, sticky='ew')

        tk.Label(form_frame, text="Donate Anonymously:").grid(row=2, column=0, sticky='w')
        self.is_anonymous_var = tk.BooleanVar(self)
        tk.Checkbutton(form_frame, variable=self.is_anonymous_var).grid(row=2, column=1, sticky='w')

        tk.Button(form_frame, text="Submit Donation", command=self.submit_donation, bg='blue', fg='white').grid(row=3, columnspan=2, pady=10)

        # My donations
        tk.Label(self, text="Your Donations (Update / Delete)", font=("Arial", 14, "underline")).pack(pady=6)
        crud_frame = tk.Frame(self)
        crud_frame.pack(padx=20, pady=6, fill='both', expand=True)

        columns = ('donation_id', 'fund_id', 'amount', 'status', 'date')
        self.my_donations_tree = ttk.Treeview(crud_frame, columns=columns, show='headings', height=8)
        for col in columns:
            self.my_donations_tree.heading(col, text=col)
            self.my_donations_tree.column(col, anchor=tk.CENTER, width=100)
        self.my_donations_tree.pack(fill='both', expand=True)
        self.my_donations_tree.bind('<<TreeviewSelect>>', self.on_donation_select)

        edit_frame = tk.Frame(self)
        edit_frame.pack(pady=6)
        tk.Label(edit_frame, text="Selected Donation ID:").grid(row=0, column=0, sticky='e')
        self.selected_donation_label = tk.Label(edit_frame, text='-')
        self.selected_donation_label.grid(row=0, column=1, sticky='w')

        tk.Label(edit_frame, text="Edit Amount:").grid(row=1, column=0, sticky='e')
        self.edit_amount_entry = tk.Entry(edit_frame, width=20)
        self.edit_amount_entry.grid(row=1, column=1, sticky='w')

        tk.Button(edit_frame, text="Update", command=self.handle_update_donation).grid(row=2, column=0, pady=6)
        tk.Button(edit_frame, text="Delete", command=self.handle_delete_donation).grid(row=2, column=1, pady=6)

        # Load initial data
        self.load_funds()
        self.load_my_donations_table()

    def load_funds(self):
        try:
            funds = self.manager.get_active_funds_list()
        except Exception:
            funds = []

        self.fund_id_map = {}
        descriptions = []
        for f in funds:
            fid = f[0]
            desc = f"{f[1]} - {f[2]} (${f[3]:.2f} needed)"
            descriptions.append(desc)
            self.fund_id_map[desc] = fid

        menu = self.fund_menu['menu']
        menu.delete(0, 'end')
        if descriptions:
            for d in descriptions:
                menu.add_command(label=d, command=lambda value=d: self.fund_var.set(value))
            self.fund_var.set(descriptions[0])
        else:
            menu.add_command(label='No active funds', command=lambda: None)
            self.fund_var.set('No active funds')

    def submit_donation(self):
        fund_description = self.fund_var.get()
        amount_str = self.amount_entry.get().strip()
        is_anonymous = bool(self.is_anonymous_var.get())

        if not amount_str:
            messagebox.showerror("Error", "Please enter a donation amount.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive number for the amount.")
            return

        success, message = self.manager.submit_donation(fund_description, amount, is_anonymous, self.fund_id_map, self.user_id)
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.is_anonymous_var.set(False)
            self.load_my_donations_table()
        else:
            messagebox.showerror("Error", message)

    def load_my_donations_table(self):
        for item in self.my_donations_tree.get_children():
            self.my_donations_tree.delete(item)
        self.my_donations_raw = {}
        self.selected_donation_id = None
        self.selected_donation_label.config(text='-')
        self.edit_amount_entry.delete(0, tk.END)

        try:
            rows = self.manager.get_my_donations(self.user_id)
        except Exception:
            rows = []

        for row in rows:
            donation_id, fund_id, donation_amount, payment_status, donation_date = row
            self.my_donations_raw[donation_id] = row
            date_str = donation_date.strftime("%Y-%m-%d") if donation_date else "N/A"
            self.my_donations_tree.insert('', tk.END, values=(donation_id, fund_id, f"{float(donation_amount):.2f}", payment_status, date_str))

    def on_donation_select(self, event):
        selection = self.my_donations_tree.selection()
        if not selection:
            return
        values = self.my_donations_tree.item(selection[0], 'values')
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
            self.edit_amount_entry.delete(0, tk.END)
            self.edit_amount_entry.insert(0, str(row[2]))

    def handle_update_donation(self):
        if not self.selected_donation_id:
            messagebox.showerror("Error", "Please select a donation first.")
            return
        amount_str = self.edit_amount_entry.get().strip()
        success, msg = self.manager.update_donation(self.user_id, self.selected_donation_id, amount_str)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_donations_table()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete_donation(self):
        if not self.selected_donation_id:
            messagebox.showerror("Error", "Please select a donation first.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete donation {self.selected_donation_id}? This may affect fund totals."):
            return
        success, msg = self.manager.delete_donation(self.user_id, self.selected_donation_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_my_donations_table()
        else:
            messagebox.showerror("Error", msg)

