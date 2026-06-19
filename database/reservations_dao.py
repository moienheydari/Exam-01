import sqlite3


def get_reservations_by_participant(participant_id):
    """Get all reservations by a participant"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, participant_id, reserved_tour_id, person_count, addit_person_1, 
                   addit_person_2, addit_person_3 FROM Reservations WHERE participant_id = ?"""
        cursor.execute(query, (participant_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_reservations_by_reserved_tour(reserved_tour_id):
    """Get all reservations for a reserved tour"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT id, participant_id, reserved_tour_id, person_count, addit_person_1, 
                   addit_person_2, addit_person_3 FROM Reservations WHERE reserved_tour_id = ?"""
        cursor.execute(query, (reserved_tour_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def create_reservation(participant_id, reserved_tour_id, person_count, 
                      addit_person_1=None, addit_person_2=None, addit_person_3=None):
    """Create a new reservation"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = """INSERT INTO Reservations (participant_id, reserved_tour_id, person_count, 
                   addit_person_1, addit_person_2, addit_person_3) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (participant_id, reserved_tour_id, person_count, 
                              addit_person_1, addit_person_2, addit_person_3))
        
        conn.commit()
        reservation_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return reservation_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None



def delete_reservation(reservation_id):
    """Delete a reservation"""
    try:
        conn = sqlite3.connect("database/space_tours.db")
        cursor = conn.cursor()
        
        query = "DELETE FROM Reservations WHERE id = ?"
        cursor.execute(query, (reservation_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
