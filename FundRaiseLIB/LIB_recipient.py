from FundRaiseDAL.DAL_recipient import (
    fetch_all_services,
    insert_new_fund,
    fetch_recipient_funds,
    update_recipient_fund,
    delete_recipient_fund,
)

class RecipientManager:
    """Handles logic for creating and managing fund requests."""
    
    def get_services_data(self):
        """Fetches all service providers for the dropdown list."""
        # Returns list of (id, name)
        return fetch_all_services()
        
    def create_fund(self, recipient_id, service_name, amount_needed_str, proof_of_charge, service_map):
        """Submits a new fund request after validation."""
        
        if service_name not in service_map:
            return False, "Validation Error: Please select a valid service provider."

        try:
            amount_needed = float(amount_needed_str)
            if amount_needed <= 0:
                return False, "Validation Error: Amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Amount Needed."

        service_id = service_map[service_name]
        
        success, db_message = insert_new_fund(
            recipient_id, service_id, amount_needed, proof_of_charge
        )
        
        if success:
            return True, "Fund Request submitted successfully! It is now pending Admin verification."
        else:
            return False, f"Database Error: Failed to submit fund request: {db_message}"


    def get_recipient_funds(self, recipient_id):
        """Return list of funds created by this recipient."""
        return fetch_recipient_funds(recipient_id)

    def update_fund(self, recipient_id, fund_id, amount_str, proof):
        """Validate and update fund fields."""
        if not fund_id:
            return False, "Error: No fund selected."

        try:
            amount_needed = float(amount_str)
            if amount_needed <= 0:
                return False, "Validation Error: Amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Amount Needed."

        success, db_message = update_recipient_fund(recipient_id, fund_id, amount_needed, proof)
        if success:
            return True, f"Fund ID {fund_id} updated successfully."
        else:
            return False, f"Database Error: Failed to update fund: {db_message}"

    def delete_fund(self, recipient_id, fund_id):
        """Delete a fund created by this recipient."""
        if not fund_id:
            return False, "Error: No fund selected."

        success, db_message = delete_recipient_fund(recipient_id, fund_id)
        if success:
            return True, f"Fund ID {fund_id} deleted successfully."
        else:
            return False, f"Database Error: Failed to delete fund: {db_message}"
