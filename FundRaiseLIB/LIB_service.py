from FundRaiseDAL import DAL_service

class ServiceManager:
    """Handles logic for updating fund documentation."""
    
    def get_funds_assigned_to_service(self, service_user_id):
        """Fetches funds assigned to this service user."""
        # Returns list of (fund_id, recipient_name, amount_needed, proof_of_charge)
        return DAL_service.fetch_service_funds(service_user_id)
        
    def update_fund_proof(self, fund_description, new_proof, service_user_id, fund_map):
        """Updates the proof of charge for a fund."""
        
        if fund_description not in fund_map:
            return False, "Please select a valid fund."
        
        # fund_map contains (fund_id, current_proof)
        fund_id, _ = fund_map[fund_description]

        if not new_proof or new_proof.strip() == "":
            return False, "Proof of Charge link cannot be empty."

        success, db_message = DAL_service.update_fund_proof_of_charge(
            fund_id, new_proof, service_user_id
        )
        
        if success:
            return True, f"Proof of Charge for Fund ID {fund_id} updated successfully!"
        else:
            return False, f"Database Error: Failed to update proof of charge: {db_message}"