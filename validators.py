import re
from datetime import datetime
import ops
import database.tours_dao as tours_dao
import database.places_dao as places_dao

def to_minutes(time_str):
    parts = time_str.split(':')
    return int(parts[0]) * 60 + int(parts[1])

def minutes_to_hm(m):
    h = (m // 60) % 24
    min_part = m % 60
    return f"{h:02d}:{min_part:02d}"

def validate_booking(selected_date, selected_time, person_count, addit_1, addit_2, addit_3, current_tour, pid):
    if not selected_date or not selected_time:
        return False, 'Please select a date and time.'

    if not current_tour:
        return False, 'Tour not found.'

    # Verify if the tour is actually offered on the selected date and time
    offered_dates = ops.get_next_dates(current_tour['schedule'], weeks=4)
    is_offered = any(str(d['date']) == selected_date and d['time'] == selected_time for d in offered_dates)
    if not is_offered:
        return False, 'This tour is not offered on the selected date and time.'

    # Validate party size and additional names
    if not 1 <= person_count <= 4:
        return False, 'Person count must be between 1 and 4.'

    if person_count >= 2 and (not addit_1 or len(addit_1.strip()) < 3):
        return False, 'Please provide a valid name for additional person 1 (minimum 3 characters).'
    if person_count >= 3 and (not addit_2 or len(addit_2.strip()) < 3):
        return False, 'Please provide a valid name for additional person 2 (minimum 3 characters).'
    if person_count >= 4 and (not addit_3 or len(addit_3.strip()) < 3):
        return False, 'Please provide a valid name for additional person 3 (minimum 3 characters).'

    new_start = to_minutes(selected_time)
    new_end = new_start + current_tour['duration']

    # Get all reservations of this participant and check for conflicts
    participant_reservations = ops.get_participant_profile_data(pid)
    for r in participant_reservations:
        if r['reserved_tour'] and r['tour'] and r['reserved_tour']['date'] == selected_date:
            exist_start = to_minutes(r['reserved_tour']['time'])
            exist_end = exist_start + r['tour']['duration']
            # Check if intervals overlap
            if new_start < exist_end and exist_start < new_end:
                return False, f"Time conflict: This tour conflicts with your reservation for '{r['tour']['title']}' ({r['reserved_tour']['time']} - {minutes_to_hm(exist_end)})."

    return True, None


def validate_cancellation(reservation_id, user_type):
    if reservation_id <= 0:
        return False, 'Invalid reservation ID.'
    if user_type != 'participant':
        return False, 'Only participants can cancel reservations.'
    return True, None


def validate_authentication(credential, password):
    if not credential or not password:
        return False, 'Please fill in all fields.'
    if len(credential) > 100 or len(password) > 100:
        return False, 'Input length exceeded.'
    return True, None


def validate_signup(user_type, first_name, last_name, email, password, languages_list, profile_img):
    if user_type not in ['participant', 'guide']:
        return False, 'Invalid account type.'

    if not first_name or not last_name or not email or not password:
        return False, 'Please fill in all required fields.'

    if len(first_name) < 2 or len(first_name) > 50 or len(last_name) < 2 or len(last_name) > 50:
        return False, 'First name and last name must be between 2 and 50 characters.'

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email) or len(email) > 100:
        return False, 'Please enter a valid email address.'

    if len(password) < 6 or len(password) > 100:
        return False, 'Password must be between 6 and 100 characters.'

    # Guide-only checks
    if user_type == 'guide':
        if not languages_list:
            return False, 'Guides must select at least one spoken language.'
        for lang in languages_list:
            if lang not in ops.LANGUAGES.keys():
                return False, f'Invalid language selection: {lang}'

        if profile_img and profile_img.filename:
            ext = profile_img.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                return False, 'Only JPG, JPEG, and PNG images are allowed for profile photos.'

    return True, None


def validate_create_tour(title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, stops, guide_languages, photo_files):
    if not title or len(title) > 100:
        return False, 'Title must be between 1 and 100 characters.'
    if not description or len(description) > 1000:
        return False, 'Description must be between 1 and 1000 characters.'

    try:
        dur_val = int(duration)
        if not 30 <= dur_val <= 600:
            raise ValueError()
    except ValueError:
        return False, 'Duration must be an integer between 30 and 600 minutes.'

    try:
        max_p = int(max_part_count)
        if not 3 <= max_p <= 50:
            raise ValueError()
    except ValueError:
        return False, 'Max participants must be an integer between 3 and 50.'

    if language not in guide_languages:
        return False, 'You must select a language that you speak.'

    # Validate meeting point
    if not new_meetpoint and not meetpoint_place_id:
        return False, 'Please specify a meeting point.'
    if meetpoint_place_id and not new_meetpoint:
        try:
            mp_id = int(meetpoint_place_id)
            if not places_dao.get_place_by_id(mp_id):
                raise ValueError()
        except ValueError:
            return False, 'Selected meeting point does not exist.'
    if new_meetpoint and len(new_meetpoint) > 100:
        return False, 'New meeting point name must be under 100 characters.'

    if not days:
        return False, 'Please select at least one day for the weekly schedule.'

    time_regex = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
    for day in days:
        time_val = form_times.get(day, '').strip()
        if not time_val or not re.match(time_regex, time_val):
            return False, f'Please enter a valid start time (HH:MM) for {day}.'

    valid_stops = [s.strip() for s in stops if s.strip()]
    if len(valid_stops) < 4:
        return False, 'You must provide at least 4 valid (non-empty) stops for the itinerary.'

    # Validate file uploads (extensions)
    for i in range(1, 6):
        photo = photo_files.get(f'photo_{i}')
        if photo and photo.filename:
            ext = photo.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                return False, f'Photo {i} must be a JPG, JPEG, or PNG file.'

    return True, None


def validate_edit_tour(title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, stops, guide_languages, photo_files, has_reservations):
    if not title or len(title) > 100:
        return False, 'Title must be between 1 and 100 characters.'
    if not description or len(description) > 1000:
        return False, 'Description must be between 1 and 1000 characters.'

    # Validate file uploads (extensions)
    for i in range(1, 6):
        photo = photo_files.get(f'photo_{i}')
        if photo and photo.filename:
            ext = photo.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                return False, f'Photo {i} must be a JPG, JPEG, or PNG file.'

    if not has_reservations:
        try:
            dur_val = int(duration)
            if not 30 <= dur_val <= 600:
                raise ValueError()
        except ValueError:
            return False, 'Duration must be an integer between 30 and 600 minutes.'

        try:
            max_p = int(max_part_count)
            if not 3 <= max_p <= 50:
                raise ValueError()
        except ValueError:
            return False, 'Max participants must be an integer between 3 and 50.'

        if language not in guide_languages:
            return False, 'You must select a language that you speak.'

        if not new_meetpoint and not meetpoint_place_id:
            return False, 'Please specify a meeting point.'
        if meetpoint_place_id and not new_meetpoint:
            try:
                mp_id = int(meetpoint_place_id)
                if not places_dao.get_place_by_id(mp_id):
                    raise ValueError()
            except ValueError:
                return False, 'Selected meeting point does not exist.'
        if new_meetpoint and len(new_meetpoint) > 100:
            return False, 'New meeting point name must be under 100 characters.'

        if not days:
            return False, 'Please select at least one day for the weekly schedule.'

        time_regex = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
        for day in days:
            time_val = form_times.get(day, '').strip()
            if not time_val or not re.match(time_regex, time_val):
                return False, f'Please enter a valid start time (HH:MM) for {day}.'

        valid_stops = [s.strip() for s in stops if s.strip()]
        if len(valid_stops) < 4:
            return False, 'You must provide at least 4 valid (non-empty) stops for the itinerary.'

    return True, None


def validate_report_tour(actual_count, expected_part_count, tour_date_str, tour_time_str, proof_img):
    try:
        count_val = int(actual_count)
        if not 0 <= count_val <= expected_part_count:
            raise ValueError()
    except ValueError:
        return False, f'Actual participant count must be an integer between 0 and {expected_part_count}.'

    try:
        tour_dt = datetime.strptime(f"{tour_date_str} {tour_time_str}", "%Y-%m-%d %H:%M")
        if datetime.now() <= tour_dt:
            return False, 'You can only report tours that have already taken place.'
    except ValueError:
        return False, 'Invalid tour date/time format.'

    if not proof_img or not proof_img.filename:
        return False, 'Proof photo is required.'

    ext = proof_img.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png']:
        return False, 'Proof photo must be a JPG, JPEG, or PNG file.'

    return True, None
