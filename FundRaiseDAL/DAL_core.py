import mysql.connector


DB_CONFIG = {
    'user': 'root',         #  CHANGE USERNAME
    'password': '',   # AND PASSWORD 
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

def authenticate_user(email, password):
    """Checks credentials and returns (user_id, user_type) if valid."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, user_type FROM Users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else (None, None)
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