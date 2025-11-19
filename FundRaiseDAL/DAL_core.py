import mysql.connector
import hashlib


# ============================================================
# Database Configuration
# ============================================================
DB_CONFIG = {
    'user': 'root',             # CHANGE USERNAME
    'password': 'Chuck!2345',   # CHANGE PASSWORD
    'host': '127.0.0.1',
    'database': 'fundraising_db'
}


def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


# ============================================================
# Database Shared Query Functions
# ============================================================
def fetch_user_by_email(email):
    """Returns (user_id, user_type, password_hash) for the given email or None."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, user_type, password_hash FROM Users WHERE email = %s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    return None


def fetch_user_by_id(user_id):
    """Returns the user row for a given user_id or None."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, name, email, user_type FROM Users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    return None


def create_user(name, email, password, user_type):
    """Creates a new user. Returns (True, user_id) or (False, error_message).

    The password is hashed with SHA-256 before storing.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            query = "INSERT INTO Users (name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, password_hash, user_type))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return True, user_id
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return False, str(err)
    return False, "Failed to connect to the database."


def authenticate_user(email, password):
    """Checks credentials and returns (user_id, user_type) if valid.

    This function fetches the stored password_hash for the user and
    compares it against the provided password after hashing with SHA-256.
    """
    row = fetch_user_by_email(email)
    if not row:
        return (None, None)

    stored_hash = row[2]  # expecting (user_id, user_type, password_hash)
    # Hash the supplied password the same way create_user does
    supplied_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Accept either a hashed password (SHA-256 hex) or legacy plaintext stored password.
    if supplied_hash == stored_hash or password == stored_hash:
        return (row[0], row[1])
    return (None, None)


def fetch_funds_data():
    """Fetches key information about all FundsNeeded for the Main Window."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS Recipient,
            s.service_name AS Service,
            f.amount_needed,
            f.amount_raised,
            f.is_fully_funded
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []


def fetch_donations_data():
    """Fetches key information about recent Donations for the Main Window."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            d.donation_id,
            d.fund_id,
            u_don.name AS Donor,
            d.donation_amount,
            d.donation_date
        FROM Donations d
        LEFT JOIN Donors r ON d.donor_id = r.user_id
        LEFT JOIN Users u_don ON r.user_id = u_don.user_id
        ORDER BY d.donation_date DESC
        LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []


def update_user_profile(user_id, name=None, phone_number=None, address=None):
    """Update basic fields in Users table for a user_id."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            fields = []
            params = []
            if name is not None:
                fields.append('name = %s')
                params.append(name)
            if phone_number is not None:
                fields.append('phone_number = %s')
                params.append(phone_number)
            if address is not None:
                fields.append('address = %s')
                params.append(address)

            if not fields:
                return True, 'No fields to update.'

            params.append(user_id)
            query = f"UPDATE Users SET {', '.join(fields)} WHERE user_id = %s"
            cursor.execute(query, tuple(params))
            conn.commit()
            return True, 'Success'
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, 'Failed to connect to the database.'