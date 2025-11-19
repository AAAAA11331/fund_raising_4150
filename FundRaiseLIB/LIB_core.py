from FundRaiseDAL import DAL_core

class AuthManager:
    """Handles login and registration logic."""
    def authenticate_user(self, email, password):
        return DAL_core.authenticate_user(email, password)

