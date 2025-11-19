from .DAL_core import get_db_connection
import mysql.connector


# ============================================================
# Helper Query Functions related to recipients role
# ============================================================

def fetch_all_services():
    """Fetches list of services (id, name) for the Recipient fund creation form."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "SELECT user_id, name FROM Users WHERE user_type = 'Service'"
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()
            conn.close()
    return []


def insert_new_fund(recipient_id, service_id, amount_needed, proof_of_charge):
    """Inserts a new fund request into the FundsNeeded table."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO FundsNeeded 
            (recipient_id, service_id, amount_needed, proof_of_charge, is_verified) 
            VALUES (%s, %s, %s, %s, FALSE)
            """
            cursor.execute(query, (recipient_id, service_id, amount_needed, proof_of_charge))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def fetch_recipient_funds(recipient_id):
    """
    Returns all funds created by this recipient.
    (fund_id, service_name, amount_needed, amount_raised, is_verified, is_fully_funded, proof_of_charge)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            SELECT
                f.fund_id,
                u_serv.name AS service_name,
                f.amount_needed,
                f.amount_raised,
                f.is_verified,
                f.is_fully_funded,
                f.proof_of_charge
            FROM FundsNeeded f
            JOIN Users u_serv ON f.service_id = u_serv.user_id
            WHERE f.recipient_id = %s
            ORDER BY f.fund_id DESC;
            """
            cursor.execute(query, (recipient_id,))
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()
            conn.close()
    return []


def update_recipient_fund(recipient_id, fund_id, new_amount_needed, new_proof):
    """Update amount_needed + proof_of_charge for a recipient's own fund."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE FundsNeeded
            SET amount_needed = %s, proof_of_charge = %s
            WHERE fund_id = %s AND recipient_id = %s
            """
            cursor.execute(query, (new_amount_needed, new_proof, fund_id, recipient_id))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def delete_recipient_fund(recipient_id, fund_id):
    """
    Delete a fund created by this recipient.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # First delete related donations
            cursor.execute("DELETE FROM Donations WHERE fund_id = %s", (fund_id,))
            # Then delete the fund
            cursor.execute(
                "DELETE FROM FundsNeeded WHERE fund_id = %s AND recipient_id = %s",
                (fund_id, recipient_id)
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


def fetch_recipient_profile(user_id):
    """Return recipient-specific profile row or None.

    Expected return: (user_id, contact_email, join_date)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, contact_email, join_date FROM Recipients WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            return row
        finally:
            cursor.close()
            conn.close()
    return None


def upsert_recipient_profile(user_id, contact_email):
    """Insert or update recipient profile.

    Returns (True, message) or (False, error)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM Recipients WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute("UPDATE Recipients SET contact_email = %s WHERE user_id = %s", (contact_email, user_id))
            else:
                cursor.execute("INSERT INTO Recipients (user_id, contact_email) VALUES (%s, %s)", (user_id, contact_email))
            conn.commit()
            return True, 'Success'
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, 'Failed to connect to the database.'
