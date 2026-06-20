import sqlite3

# Schedule format: semicolon-separated day-time pairs
# Days: SAT, SUN, MON, TUE, WED, THU, FRI
# Time: HH:MM or X (meaning not scheduled on that day)
# Example: "SAT_10:45;SUN_14:30;MON_X;TUE_16:00;WED_X;THU_11:15;FRI_X"


def get_tour_by_id(tour_id):
    """Get a tour by ID"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, title, guide_id, schedule, meetpoint_place_id, duration, 
                   language, max_part_count, description, photo_1_address, photo_2_address, 
                   photo_3_address, photo_4_address, photo_5_address FROM Tours WHERE id = ?"""
        cursor.execute(query, (tour_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_all_tours():
    """Get all tours"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, title, guide_id, schedule, meetpoint_place_id, duration, 
                   language, max_part_count, description, photo_1_address, photo_2_address, 
                   photo_3_address, photo_4_address, photo_5_address FROM Tours"""
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_tours_by_guide(guide_id):
    """Get all tours by a specific guide"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, title, guide_id, schedule, meetpoint_place_id, duration, 
                   language, max_part_count, description, photo_1_address, photo_2_address, 
                   photo_3_address, photo_4_address, photo_5_address FROM Tours WHERE guide_id = ?"""
        cursor.execute(query, (guide_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_tours_by_language(language):
    """Get all tours in a specific language"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, title, guide_id, schedule, meetpoint_place_id, duration, 
                   language, max_part_count, description, photo_1_address, photo_2_address, 
                   photo_3_address, photo_4_address, photo_5_address FROM Tours WHERE language = ?"""
        cursor.execute(query, (language,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def create_tour(title, guide_id, schedule, meetpoint_place_id, duration, language, 
                max_part_count, description, photo_1_address, photo_2_address, 
                photo_3_address, photo_4_address, photo_5_address):
    """Create a new tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = """INSERT INTO Tours (title, guide_id, schedule, meetpoint_place_id, duration, 
                   language, max_part_count, description, photo_1_address, photo_2_address, 
                   photo_3_address, photo_4_address, photo_5_address) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (title, guide_id, schedule, meetpoint_place_id, duration, 
                              language, max_part_count, description, photo_1_address, 
                              photo_2_address, photo_3_address, photo_4_address, photo_5_address))
        
        conn.commit()
        tour_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return tour_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def update_tour(tour_id, title=None, guide_id=None, schedule=None, meetpoint_place_id=None, 
                duration=None, language=None, max_part_count=None, description=None,
                photo_1_address=None, photo_2_address=None, photo_3_address=None, 
                photo_4_address=None, photo_5_address=None):
    """Update tour information"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if guide_id is not None:
            updates.append("guide_id = ?")
            values.append(guide_id)
        if schedule is not None:
            updates.append("schedule = ?")
            values.append(schedule)
        if meetpoint_place_id is not None:
            updates.append("meetpoint_place_id = ?")
            values.append(meetpoint_place_id)
        if duration is not None:
            updates.append("duration = ?")
            values.append(duration)
        if language is not None:
            updates.append("language = ?")
            values.append(language)
        if max_part_count is not None:
            updates.append("max_part_count = ?")
            values.append(max_part_count)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if photo_1_address is not None:
            updates.append("photo_1_address = ?")
            values.append(photo_1_address)
        if photo_2_address is not None:
            updates.append("photo_2_address = ?")
            values.append(photo_2_address)
        if photo_3_address is not None:
            updates.append("photo_3_address = ?")
            values.append(photo_3_address)
        if photo_4_address is not None:
            updates.append("photo_4_address = ?")
            values.append(photo_4_address)
        if photo_5_address is not None:
            updates.append("photo_5_address = ?")
            values.append(photo_5_address)
        
        if not updates:
            return False
        
        values.append(tour_id)
        query = f"UPDATE Tours SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def delete_tour(tour_id):
    """Delete a tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "DELETE FROM Tours WHERE id = ?"
        cursor.execute(query, (tour_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
