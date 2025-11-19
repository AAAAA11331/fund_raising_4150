import tkinter as tk
from tkinter import messagebox
from FundRaiseGUI.GUI_core import MainWindow, LoginWindow, RegistrationWindow 
from FundRaiseGUI.GUI_admin import AdminDashboard
from FundRaiseGUI.GUI_recipient import RecipientDashboard
from FundRaiseGUI.GUI_donor import DonorDashboard
from FundRaiseGUI.GUI_service import ServiceDashboard

DASHBOARD_CLASSES = (
    MainWindow, 
    LoginWindow, 
    RegistrationWindow, 
    AdminDashboard, 
    RecipientDashboard, 
    DonorDashboard, 
    ServiceDashboard
)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fundraising Project")
        self.geometry("800x600")
        
        self.option_add("*Button.foreground", "black")

        self.user_id = None
        self.user_role = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        for F in DASHBOARD_CLASSES:
            page_name = F.__name__
            # Pass user_id=None for dashboards that require it
            if F in (RecipientDashboard, DonorDashboard, ServiceDashboard):
                frame = F(master=container, controller=self, user_id=None) 
            else:
                frame = F(master=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainWindow)  # Start on the Main Window

    def login(self, user_id, user_role):
        self.user_id = user_id
        self.user_role = user_role

        # Update user_id in the target frame before showing it
        target_frame_name = user_role + 'Dashboard'
        if user_role in ('Recipient', 'Donor', 'Service'):
            # The dashboard classes now have their user_id updated before being shown
            self.frames[target_frame_name].user_id = user_id
        
        # Route to the appropriate dashboard, ensuring data is refreshed
        if user_role == 'Admin':
            self.show_frame(AdminDashboard)
        elif user_role == 'Recipient':
            self.show_frame(RecipientDashboard)
        elif user_role == 'Donor':
            self.show_frame(DonorDashboard)
        elif user_role == 'Service':
            self.show_frame(ServiceDashboard)
        else:
            messagebox.showerror("Error", "Role not recognized.")
            self.show_frame(LoginWindow)

    def logout(self):
        self.user_id = None
        self.user_role = None
        self.show_frame(MainWindow)
        
    def show_frame(self, cont):
        frame = self.frames[cont.__name__]
        
        # Data refresh logic for dynamic dashboards
        if cont.__name__ == 'MainWindow':
            frame.load_data()
        elif cont.__name__ in ('AdminDashboard', 'DonorDashboard', 'ServiceDashboard', 'RecipientDashboard'):
            if hasattr(frame, 'load_funds'):
                frame.load_funds() 

        frame.tkraise()
            
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
