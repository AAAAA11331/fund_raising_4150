from .DAL_core import get_db_connection
import mysql.connector

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