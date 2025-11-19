import tkinter as tk
from tkinter import messagebox
from FundRaiseLIB import LIB_service
from .GUI_core import MainWindow

class ServiceDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = LIB_service.ServiceManager() # LIB initialization
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Label(self, text="Service Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(btn_frame, text="Edit Profile", command=lambda: controller.open_profile()).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Logout", command=controller.logout).pack(side=tk.LEFT, padx=6)
        
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
        """Fetches and populates the fund selection dropdown using BLL."""
        # LIB call
        self.funds_data = self.manager.get_funds_assigned_to_service(self.user_id)
        
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
        """DELEGATE PROOF UPDATE to LIB."""
        selected_desc = self.fund_var.get()
        new_proof = self.proof_entry.get()
        
        if selected_desc not in self.fund_map or not self.user_id:
            messagebox.showerror("Error", "Please select a valid fund.")
            return
        
        # DELEGATE to LIB
        success, message = self.manager.update_fund_proof(
            selected_desc, new_proof, self.user_id, self.fund_map
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_funds()
            self.controller.show_frame(MainWindow)
        else:
            messagebox.showerror("Error", message)