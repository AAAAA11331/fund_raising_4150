from FundRaiseDAL import DAL_admin

class AdminManager:
    """Handles all admin-specific business rules."""
    
    def get_pending_funds_list(self):
        """Fetches pending funds list from DAL."""
        # Returns list of (fund_id, recipient_name, service_name, amount_needed, proof_of_charge)
        return DAL_admin.fetch_unverified_funds()
    
    def verify_fund(self, fund_id):
        """Coordinates fund verification using the Admin DAL."""
        if not fund_id:
            return False, "Error: Fund ID is missing."
        
        success = DAL_admin.update_fund_verification_status(fund_id)
        
        if success:
            return True, f"Fund ID {fund_id} has been successfully verified! It is now active for donations."
        else:
            return False, "Failed to verify fund due to a database error."

    def get_all_funds_list(self):
        """
        Returns all funds for admin management:
        (fund_id, recipient_name, service_name,
         amount_needed, amount_raised, is_verified, is_fully_funded, proof_of_charge)
        """
        return DAL_admin.fetch_all_funds()

    def update_fund(self, fund_id, new_amount_str, new_proof):
        """
        Validates and updates amount_needed + proof_of_charge for a fund.
        Returns (success: bool, message: str)
        """
        if not fund_id:
            return False, "Please select a fund to update."

        try:
            new_amount = float(new_amount_str)
            if new_amount <= 0:
                return False, "Amount Needed must be greater than zero."
        except ValueError:
            return False, "Please enter a valid number for Amount Needed."

        if new_proof is None:
            new_proof = ""
        success, db_msg = DAL_admin.update_fund_amount_and_proof(fund_id, new_amount, new_proof)
        if success:
            return True, f"Fund ID {fund_id} updated successfully."
        else:
            return False, f"Database Error while updating fund: {db_msg}"

    def delete_fund(self, fund_id):
        """
        Deletes a fund (and related donations).
        Returns (success: bool, message: str)
        """
        if not fund_id:
            return False, "Please select a fund to delete."

        success, db_msg = DAL_admin.delete_fund(fund_id)
        if success:
            return True, f"Fund ID {fund_id} deleted successfully."
        else:
            return False, f"Database Error while deleting fund: {db_msg}"
