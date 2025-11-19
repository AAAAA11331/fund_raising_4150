from FundRaiseDAL.DAL_core import get_db_connection
import mysql.connector

# ============================================================
# Helper Query Functions related to admin role
# ============================================================

def fetch_unverified_funds():
    """
    Fetches FundsNeeded records that are not yet verified (is_verified = FALSE).
    Returns list of (fund_id, recipient_name, service_name, amount_needed, proof_of_charge).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            s.service_name AS ServiceName,
            f.amount_needed,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        WHERE f.is_verified = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def update_fund_verification_status(fund_id: int) -> bool:
    """Updates a fund's is_verified status to TRUE."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "UPDATE FundsNeeded SET is_verified = TRUE WHERE fund_id = %s"
            cursor.execute(query, (fund_id,))
            conn.commit()
            return True
        except mysql.connector.Error:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False


def fetch_all_funds():
    """
    Fetches ALL FundsNeeded records for admin management.
    Returns list of:
      (fund_id, recipient_name, service_name,
       amount_needed, amount_raised, is_verified, is_fully_funded, proof_of_charge)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            s.service_name AS ServiceName,
            f.amount_needed,
            f.amount_raised,
            f.is_verified,
            f.is_fully_funded,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    return []


def update_fund_amount_and_proof(fund_id: int, new_amount: float, new_proof: str):
    """
    Updates amount_needed and proof_of_charge for a specific fund.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE FundsNeeded
            SET amount_needed = %s,
                proof_of_charge = %s
            WHERE fund_id = %s
            """
            cursor.execute(query, (new_amount, new_proof, fund_id))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def delete_fund(fund_id: int):
    """
    Deletes a fund (and its donations) from the database.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Remove dependent donations first (FK constraint)
            cursor.execute("DELETE FROM Donations WHERE fund_id = %s", (fund_id,))
            # Then delete the fund itself
            cursor.execute("DELETE FROM FundsNeeded WHERE fund_id = %s", (fund_id,))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."
