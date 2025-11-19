import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from FundRaiseLIB import LIB_admin
from FundRaiseGUI import GUI_core  

class AdminDashboard(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.admin_manager = LIB_admin.AdminManager()  # LIB initialization
        
        # Track selected fund for CRUD
        self.selected_fund_id = None
        self.all_funds_raw = {}  # fund_id -> full row

        tk.Label(self, text="🔑 Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)

        tk.Label(self, text="Funds Verification (Pending Admin Action)",
                 font=("Arial", 14, "underline")).pack(pady=10)

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

        # 3. Action Buttons for verification
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        tk.Button(button_frame, text="✅ Verify Fund", command=self.verify_fund).pack(side=tk.LEFT, padx=10)
            
        
        # Dropdown change, update proof label
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        self.load_pending_funds()

        tk.Label(self, text="Manage All Funds (Update / Delete)",
                 font=("Arial", 14, "underline")).pack(pady=10)

        crud_frame = tk.Frame(self)
        crud_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Treeview for all funds
        columns = ('fund_id', 'recipient', 'service', 'needed', 'raised',
                   'verified', 'fully_funded')
        self.all_funds_tree = ttk.Treeview(crud_frame, columns=columns,
                                           show='headings', height=8)
        for col in columns:
            self.all_funds_tree.heading(col, text=col.capitalize())
            width = 80
            if col in ('recipient', 'service'):
                width = 150
            self.all_funds_tree.column(col, anchor=tk.CENTER, width=width)

        self.all_funds_tree.grid(row=0, column=0, columnspan=3, sticky='nsew', pady=5)

        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(crud_frame, orient="vertical",
                                  command=self.all_funds_tree.yview)
        self.all_funds_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky='ns')

        # Configure grid weights
        crud_frame.grid_rowconfigure(0, weight=1)
        crud_frame.grid_columnconfigure(0, weight=1)

        # Bind selection
        self.all_funds_tree.bind("<<TreeviewSelect>>", self.on_fund_select)

        # Edit fields below the tree
        tk.Label(crud_frame, text="Selected Fund ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.selected_fund_label = tk.Label(crud_frame, text="-")
        self.selected_fund_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(crud_frame, text="Amount Needed ($):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.edit_amount_entry = tk.Entry(crud_frame, width=20)
        self.edit_amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Label(crud_frame, text="Proof of Charge (URL):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.edit_proof_entry = tk.Entry(crud_frame, width=40)
        self.edit_proof_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Buttons for update & delete
        tk.Button(crud_frame,text="💾 Update Selected Fund",command=self.handle_update_fund).grid(row=4, column=0, padx=5, pady=10, sticky='e')

        tk.Button(crud_frame,text="🗑 Delete Selected Fund",command=self.handle_delete_fund).grid(row=4, column=1, padx=5, pady=10, sticky='w')


        # Initial load of all funds table
        self.load_all_funds_table()


    def load_pending_funds(self):
        """Fetches and populates the fund selection dropdown using LIB layer."""
        self.funds_data = self.admin_manager.get_pending_funds_list()
        
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
            desc = f"ID {fund_id} for {recipient_name} ({service_name}, ${amount_needed:.2f})"
            self.fund_descriptions.append(desc)
            self.fund_map[desc] = (fund_id, proof_of_charge if proof_of_charge else "N/A")

        for d in self.fund_descriptions:
            menu.add_command(label=d, command=tk._setit(self.fund_var, d))

        self.fund_var.set(self.fund_descriptions[0])
        self.load_current_proof()

    def load_current_proof(self):
        """Loads the proof_of_charge for the currently selected fund into the label."""
        selected_desc = self.fund_var.get()
        if selected_desc in self.fund_map:
            _, current_proof = self.fund_map[selected_desc]
            self.proof_label_text.set(current_proof)
        else:
            self.proof_label_text.set("")

    def open_proof_link(self, event):
        """Opens the proof link in the user's default web browser."""
        link = self.proof_label_text.get()
        if link and link not in ('N/A', 'Loading Funds...', ''):
            try:
                webbrowser.open_new_tab(link)
            except Exception as e:
                messagebox.showerror("Browser Error", f"Could not open link: {link}\nError: {e}")
        elif link == 'N/A':
            messagebox.showinfo("No Proof", "No proof of charge has been provided by the service provider yet.")

    def verify_fund(self):
        """Uses LIB layer to verify selected fund."""
        selected_desc = self.fund_var.get()
        if selected_desc not in self.fund_map:
            messagebox.showerror("Error", "Please select a valid fund to verify.")
            return

        fund_id, current_proof = self.fund_map[selected_desc]

        if current_proof == 'N/A':
            if not messagebox.askyesno(
                "Confirm Verification",
                "No proof of charge has been provided for this fund. Do you still wish to verify it?"
            ):
                return

        success, msg = self.admin_manager.verify_fund(fund_id)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

        # Refresh both views after verification
        self.load_pending_funds()
        self.load_all_funds_table()

    def load_all_funds_table(self):
        """Loads all funds into the Treeview for update/delete."""
        # Clear current rows
        for item in self.all_funds_tree.get_children():
            self.all_funds_tree.delete(item)

        self.all_funds_raw = {}
        self.selected_fund_id = None
        self.selected_fund_label.config(text="-")
        self.edit_amount_entry.delete(0, tk.END)
        self.edit_proof_entry.delete(0, tk.END)

        rows = self.admin_manager.get_all_funds_list()
        for row in rows:
            (fund_id, recipient_name, service_name,
             amount_needed, amount_raised, is_verified,
             is_fully_funded, proof_of_charge) = row

            self.all_funds_raw[fund_id] = row

            self.all_funds_tree.insert(
                '', tk.END,
                values=(
                    fund_id,
                    recipient_name,
                    service_name,
                    f"{amount_needed:.2f}",
                    f"{amount_raised:.2f}",
                    "YES" if is_verified else "NO",
                    "YES" if is_fully_funded else "NO",
                )
            )

    def on_fund_select(self, event):
        """When admin selects a row, load into edit fields."""
        selection = self.all_funds_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        values = self.all_funds_tree.item(item_id, 'values')
        if not values:
            return

        try:
            fund_id = int(values[0])
        except ValueError:
            return

        self.selected_fund_id = fund_id
        self.selected_fund_label.config(text=str(fund_id))

        row = self.all_funds_raw.get(fund_id)
        if row:
            amount_needed = row[3]
            proof = row[7] if row[7] is not None else ""
            self.edit_amount_entry.delete(0, tk.END)
            self.edit_amount_entry.insert(0, str(amount_needed))
            self.edit_proof_entry.delete(0, tk.END)
            self.edit_proof_entry.insert(0, proof)

    def handle_update_fund(self):
        """Triggered by 'Update Selected Fund' button."""
        if not self.selected_fund_id:
            messagebox.showerror("Error", "Please select a fund from the table first.")
            return

        amount_str = self.edit_amount_entry.get()
        proof = self.edit_proof_entry.get()

        success, msg = self.admin_manager.update_fund(self.selected_fund_id, amount_str, proof)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_all_funds_table()
            self.load_pending_funds()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete_fund(self):
        """Triggered by 'Delete Selected Fund' button."""
        if not self.selected_fund_id:
            messagebox.showerror("Error", "Please select a fund from the table first.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Fund ID {self.selected_fund_id}? "
            f"This will also remove all associated donations."
        ):
            return

        success, msg = self.admin_manager.delete_fund(self.selected_fund_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_all_funds_table()
            self.load_pending_funds()
        else:
            messagebox.showerror("Error", msg)
