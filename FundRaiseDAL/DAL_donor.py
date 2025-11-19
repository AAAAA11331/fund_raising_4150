from .DAL_core import get_db_connection
import mysql.connector


def fetch_active_funds():
    """Fetches active, unfulfilled funds for the Donor dashboard.

    Returns list of tuples:
    (fund_id, fund_description, amount_needed, amount_raised, recipient_name)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            SELECT
                f.fund_id,
                CONCAT('Fund ID ', f.fund_id, ': ', u_rec.name, ' (', s.name, ' - $', f.amount_needed, ')') AS fund_description,
                f.amount_needed,
                f.amount_raised,
                u_rec.name AS recipient_name
            FROM FundsNeeded f
            JOIN Users u_rec ON f.recipient_id = u_rec.user_id
            JOIN Users s ON f.service_id = s.user_id
            WHERE f.is_verified = TRUE
              AND f.is_fully_funded = FALSE
            ORDER BY f.fund_id DESC;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()
            conn.close()
    return []


def execute_donation_transaction(fund_id, donor_id_to_insert, donation_amount):
    """Executes the two-step transaction (INSERT Donation and UPDATE FundsNeeded)."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 1. Insert into Donations table
            donation_query = """
            INSERT INTO Donations 
            (fund_id, donor_id, donation_amount, payment_status) 
            VALUES (%s, %s, %s, 'Completed')
            """
            cursor.execute(donation_query, (fund_id, donor_id_to_insert, donation_amount))

            # 2. Update FundsNeeded table
            update_fund_query = """
            UPDATE FundsNeeded SET 
                amount_raised = amount_raised + %s, 
                is_fully_funded = IF((amount_raised + %s) >= amount_needed, TRUE, FALSE)
            WHERE fund_id = %s
            """
            cursor.execute(update_fund_query, (donation_amount, donation_amount, fund_id))

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
    """Returns this donor's donations as a list of tuples:
    (donation_id, fund_id, donation_amount, payment_status, donation_date)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
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
            return rows
        finally:
            cursor.close()
            conn.close()
    return []


def update_donation_amount(donor_user_id, donation_id, new_amount):
    """Update this donor's donation amount."""
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
    """Delete this donor's donation."""
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


def fetch_donor_profile(user_id):
    """Return donor-specific profile row or None.

    Expected return: (user_id, is_anonymous_default, join_date)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, is_anonymous_default, join_date FROM Donors WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            return row
        finally:
            cursor.close()
            conn.close()
    return None


def upsert_donor_profile(user_id, is_anonymous_default=False):
    """Insert or update donor profile row."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM Donors WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute("UPDATE Donors SET is_anonymous_default = %s WHERE user_id = %s", (1 if is_anonymous_default else 0, user_id))
            else:
                cursor.execute("INSERT INTO Donors (user_id, is_anonymous_default) VALUES (%s, %s)", (user_id, 1 if is_anonymous_default else 0))
            conn.commit()
            return True, 'Success'
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, 'Failed to connect to the database.'
