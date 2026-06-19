import sqlite3


def get_tour_visiting_places_by_tour(tour_id):
    """Get all places visited by a tour, ordered by visit order"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT tour_id, place_id, [order] FROM Tour_Visiting_Places 
                   WHERE tour_id = ? ORDER BY [order] ASC"""
        cursor.execute(query, (tour_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def add_place_to_tour(tour_id, place_id, order):
    """Add a place to a tour's itinerary"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "INSERT INTO Tour_Visiting_Places (tour_id, place_id, [order]) VALUES (?, ?, ?)"
        cursor.execute(query, (tour_id, place_id, order))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False