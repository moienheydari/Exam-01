# Space Tours Database - Models and DAOs Summary

This document describes the models and Data Access Objects (DAOs) created for the space_tours database.

## Database Schema Overview

The space_tours.db SQLite database contains the following tables:

- **Participants**: Tourist users who book tours
- **Guides**: Tour guide professionals  
- **Admins**: Administrative users
- **Tours**: Tour offerings/templates
- **Reserved_Tours**: Specific tour instances (with date/time)
- **Reservations**: Bookings/reservations by participants
- **Places**: Tourist destinations/locations
- **Tour_Visiting_Places**: Junction table linking tours to places they visit

---

## Models (`database/models.py`)

### Core Models

#### `User` (Base Class)
Base user model extending Flask-Login's UserMixin for authentication.
- `id`: Unique identifier
- `first_name`, `last_name`: Name components
- `email`: Email address
- `password`: Hashed password
- `profile_img`: Optional profile image path

#### `Participant(User)`
Tourist/participant model inheriting from User.
- All User properties
- `user_type = "participant"`

#### `Guide(User)`
Tour guide model inheriting from User.
- All User properties
- `languages`: Languages spoken by the guide (NUMERIC field)
- `user_type = "guide"`

#### `Admin(UserMixin)`
Administrative user model.
- `id`: Unique identifier
- `username`: Admin username
- `password`: Admin password
- `user_type = "admin"`

### Domain Models

#### `Place`
Tourist destination/location.
- `id`: Unique identifier
- `name`: Place name/description

#### `Tour`
Tour offering template.
- `id`: Unique identifier
- `title`: Tour title
- `guide_id`: ID of the guide leading this tour
- `schedule`: Tour schedule information
- `meetpoint_place_id`: Meeting point location
- `duration`: Tour duration
- `language`: Language the tour is conducted in
- `max_part_count`: Maximum participant count
- `description`: Tour description
- `photos`: List of 5 photo addresses

#### `ReservedTour`
Specific tour instance scheduled for a particular date and time.
- `id`: Unique identifier
- `tour_id`: Reference to base Tour
- `date`: Tour date
- `time`: Tour time
- `actual_part_count`: Actual number of participants (nullable)
- `proof_img_address`: Photo proof of tour completion
- `reported`: Flag indicating if tour was reported/canceled

#### `Reservation`
Participant booking for a reserved tour.
- `id`: Unique identifier
- `participant_id`: Reference to Participant
- `reserved_tour_id`: Reference to ReservedTour
- `person_count`: Number of people in reservation
- `additional_persons`: List of 3 additional person names/details
- `valid`: Boolean flag for reservation validity

#### `TourVisitingPlace`
Junction table linking tours to places in their itinerary.
- `tour_id`: Tour ID
- `place_id`: Place ID
- `order`: Sequence order of place in tour itinerary

---

## Data Access Objects (DAOs)

### `participants_dao.py`
Functions for participant/tourist management:
- `get_participant_by_id(id)` - Retrieve by ID
- `get_participant_by_email(email)` - Retrieve by email
- `get_all_participants()` - List all participants
- `create_participant(...)` - Create new participant
- `update_participant(...)` - Update participant info
- `delete_participant(id)` - Delete participant
- `get_id_by_email(email)` - Get ID by email (utility)

### `guides_dao.py`
Functions for tour guide management:
- `get_guide_by_id(id)` - Retrieve by ID
- `get_guide_by_email(email)` - Retrieve by email
- `get_all_guides()` - List all guides
- `create_guide(...)` - Create new guide
- `update_guide(...)` - Update guide info
- `delete_guide(id)` - Delete guide
- `get_id_by_email(email)` - Get ID by email (utility)

### `admins_dao.py`
Functions for admin user management:
- `get_admin_by_id(id)` - Retrieve by ID
- `get_admin_by_username(username)` - Retrieve by username
- `get_all_admins()` - List all admins
- `create_admin(username, password)` - Create new admin
- `update_admin(...)` - Update admin info
- `delete_admin(id)` - Delete admin

### `tours_dao.py`
Functions for tour offering management:
- `get_tour_by_id(id)` - Retrieve by ID
- `get_all_tours()` - List all tours
- `get_tours_by_guide(guide_id)` - List tours by specific guide
- `get_tours_by_language(language)` - List tours in specific language
- `create_tour(...)` - Create new tour
- `update_tour(...)` - Update tour info
- `delete_tour(id)` - Delete tour

### `places_dao.py`
Functions for place/location management:
- `get_place_by_id(id)` - Retrieve by ID
- `get_all_places()` - List all places
- `create_place(name)` - Create new place
- `update_place(id, name)` - Update place info
- `delete_place(id)` - Delete place

### `reserved_tours_dao.py`
Functions for reserved tour instance management:
- `get_reserved_tour_by_id(id)` - Retrieve by ID
- `get_all_reserved_tours()` - List all reserved tours
- `get_reserved_tours_by_tour(tour_id)` - List instances of a tour
- `get_reserved_tours_by_date(date)` - List tours on specific date
- `create_reserved_tour(...)` - Create new reserved tour instance
- `update_reserved_tour(...)` - Update reserved tour info
- `delete_reserved_tour(id)` - Delete reserved tour

### `reservations_dao.py`
Functions for participant booking management:
- `get_reservation_by_id(id)` - Retrieve by ID
- `get_all_reservations()` - List all reservations
- `get_reservations_by_participant(participant_id)` - List bookings by participant
- `get_reservations_by_reserved_tour(reserved_tour_id)` - List bookings for a tour instance
- `create_reservation(...)` - Create new reservation
- `update_reservation(...)` - Update reservation info
- `delete_reservation(id)` - Delete reservation

### `tour_visiting_places_dao.py`
Functions for tour itinerary management:
- `get_tour_visiting_places_by_tour(tour_id)` - Get places visited by a tour (ordered)
- `get_tour_visiting_place(tour_id, place_id)` - Get specific tour-place association
- `get_tours_visiting_place(place_id)` - Get all tours visiting a place
- `add_place_to_tour(tour_id, place_id, order)` - Add place to tour itinerary
- `update_place_order(tour_id, place_id, order)` - Update visit sequence
- `remove_place_from_tour(tour_id, place_id)` - Remove place from tour
- `remove_all_places_from_tour(tour_id)` - Clear entire tour itinerary

### Legacy DAOs (for backwards compatibility)

#### `users_dao.py`
Updated to work with Participants table. Provides:
- `new_user(...)` - Create new participant
- `get_id_by_email(email)` - Get participant ID by email
- `get_user_by_id(id)` - Retrieve participant by ID
- `get_user_by_email(email)` - Retrieve participant by email
- `get_all_users()` - List all participants
- `delete_user(id)` - Delete participant

#### `tutors_dao.py`
Updated to work with Guides table. Provides:
- `get_tutors()` - List all guides
- `new_tutor(...)` - Create new guide
- `get_tutor_by_id(id)` - Retrieve guide by ID
- `get_tutor_by_email(email)` - Retrieve guide by email
- `get_id_by_email(email)` - Get guide ID by email
- `update_tutor(...)` - Update guide info
- `delete_tutor(id)` - Delete guide

---

## Database Connection

All DAOs use the `database/space_tours.db` SQLite database. The connection string used is:
```python
conn = sqlite3.connect("database/space_tours.db")
```

---

## Error Handling

All DAO methods include try-except blocks for SQLite error handling. Errors are logged to console and appropriate return values (None, False, or empty list) are returned on failure.

---

## Usage Example

```python
from database import participants_dao, tours_dao, guides_dao

# Create a new participant
participant_id = participants_dao.create_participant(
    "John", "Doe", "john@example.com", "hashedpassword"
)

# Get all tours
all_tours = tours_dao.get_all_tours()

# Get tours by specific guide
guide_id = 1
guide_tours = tours_dao.get_tours_by_guide(guide_id)

# Create a reserved tour
reserved_tour_id = reserved_tours_dao.create_reserved_tour(
    tour_id=1, 
    date="2024-07-15", 
    time="10:00 AM"
)

# Make a reservation
reservation_id = reservations_dao.create_reservation(
    participant_id=participant_id,
    reserved_tour_id=reserved_tour_id,
    person_count=2
)
```

---

## Notes

- All DAOs follow a consistent pattern for CRUD operations
- Primary key ID values are auto-generated by SQLite
- The `get_id_by_email()` utility is available in both participants_dao and guides_dao
- Update functions use optional parameters to allow partial updates
- List functions return empty lists on error rather than None
- Foreign key relationships are maintained at the application level (not enforced at DB level in this schema)
