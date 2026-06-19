import sqlite3


def get_participant_by_id(participant_id):
    """Get a participant by ID"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, first_name, last_name, email, password FROM Participants WHERE id = ?"
        cursor.execute(query, (participant_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_participant_by_email(email):
    """Get a participant by email"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, first_name, last_name, email, password FROM Participants WHERE email = ?"
        cursor.execute(query, (email,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def create_participant(first_name, last_name, email, password):
    """Create a new participant"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "INSERT INTO Participants (first_name, last_name, email, password) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (first_name, last_name, email, password))
        
        conn.commit()
        participant_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return participant_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None