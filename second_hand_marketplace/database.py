import mysql.connector

def create_connection():
    """Create and return a new database connection."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=4322,
            user="root",
            password="1125",
            database="secondhand_marketplace",
            autocommit=True  
        )
        print("Database connection established!")
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None


conn = create_connection()
