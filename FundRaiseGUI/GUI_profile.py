import tkinter as tk
from tkinter import messagebox
from FundRaiseLIB import LIB_core


class ProfileWindow(tk.Frame):
    def __init__(self, master, controller, user_id=None):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.user_role = None
        self.pm = LIB_core.ProfileManager()

        tk.Label(self, text="Edit Profile", font=("Arial", 18, "bold")).pack(pady=8)

        top_frame = tk.Frame(self)
        top_frame.pack(pady=6)
        tk.Button(top_frame, text="Save", command=self.save_profile, bg='green', fg='white').pack(side=tk.LEFT, padx=6)
        tk.Button(top_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=6)
        tk.Button(top_frame, text="Logout", command=controller.logout).pack(side=tk.LEFT, padx=6)

        form = tk.Frame(self)
        form.pack(padx=20, pady=10, fill='x')

        tk.Label(form, text="Full Name:").grid(row=0, column=0, sticky='e')
        self.name_entry = tk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, sticky='w')

        tk.Label(form, text="Email:").grid(row=1, column=0, sticky='e')
        self.email_label = tk.Label(form, text="")
        self.email_label.grid(row=1, column=1, sticky='w')

        tk.Label(form, text="Phone Number:").grid(row=2, column=0, sticky='e')
        self.phone_entry = tk.Entry(form, width=40)
        self.phone_entry.grid(row=2, column=1, sticky='w')

        tk.Label(form, text="Address:").grid(row=3, column=0, sticky='e')
        self.address_entry = tk.Entry(form, width=60)
        self.address_entry.grid(row=3, column=1, sticky='w')

        # Role-specific area
        self.role_frame = tk.LabelFrame(self, text="Role-specific settings")
        self.role_frame.pack(padx=20, pady=10, fill='x')

        # Recipient
        self.recipient_contact_label = tk.Label(self.role_frame, text="Contact Email:")
        self.recipient_contact_entry = tk.Entry(self.role_frame, width=40)

        # Donor
        self.donor_anon_var = tk.BooleanVar(self)
        self.donor_anon_check = tk.Checkbutton(self.role_frame, text="Default to anonymous donations", variable=self.donor_anon_var)

        # Service
        self.service_name_label = tk.Label(self.role_frame, text="Service Name:")
        self.service_name_entry = tk.Entry(self.role_frame, width=40)
        self.service_desc_label = tk.Label(self.role_frame, text="Service Description:")
        self.service_desc_entry = tk.Entry(self.role_frame, width=60)
        self.service_tax_label = tk.Label(self.role_frame, text="Tax ID Number:")
        self.service_tax_entry = tk.Entry(self.role_frame, width=40)

    def cancel(self):
        self.controller.show_frame(type(self.controller.frames['MainWindow']))

    def load_profile(self):
        if not self.controller.user_id:
            messagebox.showerror("Error", "No user logged in.")
            return
        self.user_id = self.controller.user_id
        profile = self.pm.get_profile(self.user_id)
        if not profile:
            messagebox.showerror("Error", "Could not load profile.")
            return

        # Common fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, profile.get('name', '') or '')
        self.email_label.config(text=profile.get('email', '') or '')
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, profile.get('phone_number', '') or '')
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, profile.get('address', '') or '')

        # Role-specific
        role = profile.get('role')
        self.user_role = role
        for w in self.role_frame.winfo_children():
            w.grid_forget()

        if role == 'Recipient':
            rp = profile.get('role_profile') or {}
            self.recipient_contact_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.recipient_contact_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.recipient_contact_entry.delete(0, tk.END)
            self.recipient_contact_entry.insert(0, rp.get('contact_email', '') if rp else '')

        elif role == 'Donor':
            dp = profile.get('role_profile') or {}
            self.donor_anon_check.grid(row=0, column=0, sticky='w', padx=5, pady=2)
            self.donor_anon_var.set(bool(dp.get('is_anonymous_default', False)))

        elif role == 'Service':
            sp = profile.get('role_profile') or {}
            self.service_name_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.service_name_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.service_desc_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
            self.service_desc_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
            self.service_tax_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
            self.service_tax_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)
            self.service_name_entry.delete(0, tk.END)
            self.service_name_entry.insert(0, sp.get('service_name', '') if sp else '')
            self.service_desc_entry.delete(0, tk.END)
            self.service_desc_entry.insert(0, sp.get('service_description', '') if sp else '')
            self.service_tax_entry.delete(0, tk.END)
            self.service_tax_entry.insert(0, sp.get('tax_id_number', '') if sp else '')

    def save_profile(self):
        if not self.user_id:
            messagebox.showerror("Error", "No user logged in.")
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        role = self.user_role
        role_data = {}
        if role == 'Recipient':
            role_data['contact_email'] = self.recipient_contact_entry.get().strip()
        elif role == 'Donor':
            role_data['is_anonymous_default'] = bool(self.donor_anon_var.get())
        elif role == 'Service':
            role_data['service_name'] = self.service_name_entry.get().strip()
            role_data['service_description'] = self.service_desc_entry.get().strip()
            role_data['tax_id_number'] = self.service_tax_entry.get().strip()

        ok, msg = self.pm.update_profile(self.user_id, name=name, phone_number=phone, address=address, role=role, role_data=role_data)
        if ok:
            messagebox.showinfo("Success", "Profile saved.")
            self.controller.show_frame(type(self.controller.frames['MainWindow']))
        else:
            messagebox.showerror("Error", msg)
