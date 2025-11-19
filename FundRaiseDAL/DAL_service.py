from .DAL_core import get_db_connection
import mysql.connector
# ============================================================
# Helper Query Functions related to service role
# ============================================================
def fetch_service_funds(service_user_id):
    """Fetches funds where the service provider is the logged-in user."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            f.amount_needed,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        WHERE f.service_id = %s
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query, (service_user_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        # Returns list of (fund_id, recipient_name, amount_needed, proof_of_charge)
        return data
    return []

def update_fund_proof_of_charge(fund_id, new_proof, service_user_id):
    """Updates the proof_of_charge link for a specific fund."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE FundsNeeded 
            SET proof_of_charge = %s
            WHERE fund_id = %s AND service_id = %s
            """
            cursor.execute(query, (new_proof, fund_id, service_user_id))
            conn.commit()
            return True, "Success"
            
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def fetch_service_profile(user_id):
    """Return service-specific profile row or None.

    Expected return: (user_id, service_name, service_description, tax_id_number)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, service_name, service_description, tax_id_number FROM Services WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            return row
        finally:
            cursor.close()
            conn.close()
    return None


def upsert_service_profile(user_id, service_name, service_description, tax_id_number):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM Services WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute(
                    "UPDATE Services SET service_name = %s, service_description = %s, tax_id_number = %s WHERE user_id = %s",
                    (service_name, service_description, tax_id_number, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO Services (user_id, service_name, service_description, tax_id_number) VALUES (%s, %s, %s, %s)",
                    (user_id, service_name, service_description, tax_id_number)
                )
            conn.commit()
            return True, 'Success'
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, 'Failed to connect to the database.'