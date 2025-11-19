from .DAL_core import get_db_connection
import mysql.connector


def fetch_active_funds():
    """
    Fetches active, unfulfilled funds for the Donor dashboard.

    Returns list of tuples:
    (fund_id, fund_description, amount_needed, amount_raised, recipient_name)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT 
            f.fund_id, 
            CONCAT(
                f.fund_id, ': ', u_rec.name,
                ' (', s.name, ' - $', f.amount_needed, ')'
            ) AS fund_description,
            f.amount_needed,
            f.amount_raised,
            u_rec.name AS recipient_name
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Users s ON f.service_id = s.user_id
        WHERE f.is_verified = TRUE
          AND f.is_fully_funded = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []


def execute_donation_transaction(fund_id, donor_id_to_insert, donation_amount):
    """
    Insert a donation record.

    We ONLY touch the Donations table here.
    Any update to FundsNeeded (amount_raised / is_fully_funded)
    should be handled by database triggers or separate logic.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            donation_query = """
            INSERT INTO Donations 
                (fund_id, donor_id, donation_amount, payment_status) 
            VALUES (%s, %s, %s, 'Completed')
            """
            cursor.execute(donation_query, (fund_id, donor_id_to_insert, donation_amount))

            conn.commit()
            return True, "Success"

        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def fetch_donations_for_donor(donor_user_id):
    """
    Returns this donor's donations as a list of tuples:
    (donation_id, fund_id, donation_amount, payment_status, donation_date)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            d.donation_id,
            d.fund_id,
            d.donation_amount,
            d.payment_status,
            d.donation_date
        FROM Donations d
        WHERE d.donor_id = %s
        ORDER BY d.donation_date DESC;
        """
        cursor.execute(query, (donor_user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    return []


def update_donation_amount(donor_user_id, donation_id, new_amount):
    """
    Update this donor's donation amount.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Check that the donation belongs to this donor
            cursor.execute(
                "SELECT donation_amount, fund_id FROM Donations "
                "WHERE donation_id = %s AND donor_id = %s",
                (donation_id, donor_user_id)
            )
            row = cursor.fetchone()
            if not row:
                return False, "Donation not found or does not belong to this donor."

            # Update donation amount
            cursor.execute(
                "UPDATE Donations SET donation_amount = %s "
                "WHERE donation_id = %s AND donor_id = %s",
                (new_amount, donation_id, donor_user_id)
            )

            conn.commit()
            return True, "Success"

        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def delete_donation_record(donor_user_id, donation_id):
    """
    Delete this donor's donation.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Make sure the donation belongs to this donor
            cursor.execute(
                "SELECT donation_amount, fund_id FROM Donations "
                "WHERE donation_id = %s AND donor_id = %s",
                (donation_id, donor_user_id)
            )
            row = cursor.fetchone()
            if not row:
                return False, "Donation not found or does not belong to this donor."

            # Delete the donation
            cursor.execute(
                "DELETE FROM Donations WHERE donation_id = %s AND donor_id = %s",
                (donation_id, donor_user_id)
            )

            conn.commit()
            return True, "Success"

        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."
