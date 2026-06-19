import sqlite3

# Language codes:
# eng = English
# it = Italian
# sp = Spanish
# por = Portuguese
# ger = German


def get_guide_by_id(guide_id):
    """Get a guide by ID"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, first_name, last_name, email, password, languages, profile_img_address FROM Guides WHERE id = ?"
        cursor.execute(query, (guide_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_guide_by_email(email):
    """Get a guide by email"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, first_name, last_name, email, password, languages, profile_img_address FROM Guides WHERE email = ?"
        cursor.execute(query, (email,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def create_guide(first_name, last_name, email, password, languages, profile_img_address=None):
    """Create a new guide"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "INSERT INTO Guides (first_name, last_name, email, password, languages, profile_img_address) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (first_name, last_name, email, password, languages, profile_img_address))
        
        conn.commit()
        guide_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return guide_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
