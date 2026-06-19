import sqlite3


def get_admin_by_username(username):
    """Get an admin by username"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, username, password FROM Admins WHERE username = ?"
        cursor.execute(query, (username,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def create_admin(username, password):
    """Create a new admin"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "INSERT INTO Admins (username, password) VALUES (?, ?)"
        cursor.execute(query, (username, password))
        
        conn.commit()
        admin_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return admin_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None