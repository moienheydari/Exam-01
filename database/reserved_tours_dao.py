import sqlite3


def get_reserved_tour_by_id(reserved_tour_id):
    """Get a reserved tour by ID"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, tour_id, date, time, actual_part_count, expected_part_count, proof_img_address, reported 
                   FROM Reserved_Tours WHERE id = ?"""
        cursor.execute(query, (reserved_tour_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_reserved_tours_by_tour(tour_id):
    """Get all reserved tours for a specific tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, tour_id, date, time, actual_part_count, expected_part_count, proof_img_address, reported 
                   FROM Reserved_Tours WHERE tour_id = ?"""
        cursor.execute(query, (tour_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def create_reserved_tour(tour_id, date, time, expected_part_count, actual_part_count=None, 
                        proof_img_address=None, reported=0):
    """Create a new reserved tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = """INSERT INTO Reserved_Tours (tour_id, date, time, expected_part_count, actual_part_count, 
                   proof_img_address, reported) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (tour_id, date, time, expected_part_count, actual_part_count, proof_img_address, reported))
        
        conn.commit()
        reserved_tour_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return reserved_tour_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def update_reserved_tour(reserved_tour_id, tour_id=None, date=None, time=None, 
                        expected_part_count=None, actual_part_count=None, proof_img_address=None, reported=None):
    """Update reserved tour information. If expected_part_count is 0, delete the row."""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        # If expected_part_count is being set to 0, delete the row
        if expected_part_count == 0:
            query = "DELETE FROM Reserved_Tours WHERE id = ?"
            cursor.execute(query, (reserved_tour_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        
        updates = []
        values = []
        
        if tour_id is not None:
            updates.append("tour_id = ?")
            values.append(tour_id)
        if date is not None:
            updates.append("date = ?")
            values.append(date)
        if time is not None:
            updates.append("time = ?")
            values.append(time)
        if expected_part_count is not None:
            updates.append("expected_part_count = ?")
            values.append(expected_part_count)
        if actual_part_count is not None:
            updates.append("actual_part_count = ?")
            values.append(actual_part_count)
        if proof_img_address is not None:
            updates.append("proof_img_address = ?")
            values.append(proof_img_address)
        if reported is not None:
            updates.append("reported = ?")
            values.append(reported)
        
        if not updates:
            return False
        
        values.append(reserved_tour_id)
        query = f"UPDATE Reserved_Tours SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def delete_reserved_tour(reserved_tour_id):
    """Delete a reserved tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "DELETE FROM Reserved_Tours WHERE id = ?"
        cursor.execute(query, (reserved_tour_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_reserved_tour_by_tour_and_date(tour_id, date_str):
    """Get a reserved tour for a specific tour and date (unique per tour+date)"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, tour_id, date, time, actual_part_count, expected_part_count, 
                   proof_img_address, reported FROM Reserved_Tours WHERE tour_id = ? AND date = ?"""
        cursor.execute(query, (tour_id, date_str))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
