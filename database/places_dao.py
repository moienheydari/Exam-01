import sqlite3


def get_place_by_id(place_id):
    """Get a place by ID"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, name FROM Places WHERE id = ?"
        cursor.execute(query, (place_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_place_by_name(name):
    """Get a place by name"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, name FROM Places WHERE name = ?"
        cursor.execute(query, (name,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_all_places():
    """Get all places"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT id, name FROM Places"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def create_place(name):
    """Create a new place"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "INSERT INTO Places (name) VALUES (?)"
        cursor.execute(query, (name,))
        
        conn.commit()
        place_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return place_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None