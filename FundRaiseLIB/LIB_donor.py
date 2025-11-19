from FundRaiseDAL import DAL_donor

class DonorManager:
    """Business logic for donor operations (view funds, donate, manage own donations)."""


    def get_active_funds_list(self):
        """
        Fetches active funds for donation.
        Returns list of (fund_id, description, needed, raised, recipient_name).
        """
        return DAL_donor.fetch_active_funds()

    def submit_donation(self, fund_description, donation_amount_str,
                        is_anonymous, fund_id_map, donor_user_id):
        """
        Validate and submit a donation.
        """
        if fund_description not in fund_id_map:
            return False, "Validation Error: Please select a valid active fund."

        try:
            donation_amount = float(donation_amount_str)
            if donation_amount <= 0:
                return False, "Validation Error: Donation amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Donation Amount."

        fund_id = fund_id_map[fund_description]
        donor_id_to_insert = None if is_anonymous else donor_user_id

        success, db_message = DAL_donor.execute_donation_transaction(
            fund_id, donor_id_to_insert, donation_amount
        )

        if success:
            return True, f"Donation of ${donation_amount:.2f} submitted successfully to Fund ID {fund_id}!"
        else:
            return False, f"Database Error: Failed to submit donation: {db_message}"


    def get_my_donations(self, donor_user_id):
        """Return this donor's donations."""
        return DAL_donor.fetch_donations_for_donor(donor_user_id)

    def update_donation(self, donor_user_id, donation_id, new_amount_str):
        """Validate and update a donation amount."""
        try:
            new_amount = float(new_amount_str)
            if new_amount <= 0:
                return False, "Validation Error: Amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Donation Amount."

        success, db_message = DAL_donor.update_donation_amount(donor_user_id, donation_id, new_amount)
        if success:
            return True, f"Donation ID {donation_id} updated successfully."
        else:
            return False, f"Database Error: Failed to update donation: {db_message}"

    def delete_donation(self, donor_user_id, donation_id):
        """Delete a donation made by this donor."""
        success, db_message = DAL_donor.delete_donation_record(donor_user_id, donation_id)
        if success:
            return True, f"Donation ID {donation_id} deleted successfully."
        else:
            return False, f"Database Error: Failed to delete donation: {db_message}"
