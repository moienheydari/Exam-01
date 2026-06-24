from datetime import date, datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import Guide, Participant, Admin
import database.guides_dao as guides_dao
import database.participants_dao as participants_dao
import database.admins_dao as admins_dao
import database.tours_dao as tours_dao
import database.places_dao as places_dao
import database.reservations_dao as reservations_dao
import database.reserved_tours_dao as reserved_tours_dao
import database.tour_visiting_places_dao as tvp_dao

LANGUAGES = {'English': 'eng', 'Italian': 'it', 'Spanish': 'sp', 'Portuguese': 'por', 'German': 'ger'}
DAY_ORDER = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
DAY_WEEKDAY = {'SAT': 5, 'SUN': 6, 'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4}


def parse_schedule(schedule_str):
    """Parse 'SAT_10:45;SUN_X;MON_X;...' into {day: time_or_None}"""
    result = {}
    if not schedule_str:
        return result
    for part in schedule_str.split(';'):
        if '_' in part:
            day, time = part.split('_', 1)
            result[day] = None if time == 'X' else time
    return result


def get_week_dates(week_offset=0, selected_date=None):
    """Return {day_name: date} for a 7-day window.
    If selected_date is given it is used to get the Monday of its week; otherwise offset from current Monday."""
    if selected_date is not None:
        week_start = selected_date - timedelta(days=selected_date.weekday())
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    return {day: week_start + timedelta(days=i) for i, day in enumerate(DAY_ORDER)}


def get_next_dates(schedule_str, weeks=4):
    """Return list of upcoming {date, time, day} for the next N weeks based on schedule"""
    schedule = parse_schedule(schedule_str)
    today = date.today()
    result = []
    for day, time in schedule.items():
        if time is None:
            continue
        target_wd = DAY_WEEKDAY[day]
        days_ahead = (target_wd - today.weekday()) % 7
        first_occurrence = today + timedelta(days=days_ahead)
        for week in range(weeks):
            occurrence = first_occurrence + timedelta(weeks=week)
            result.append({'date': occurrence, 'time': time, 'day': day})
    result.sort(key=lambda x: x['date'])
    return result


def get_user_by_prefixed_id(user_id):
    """Load user from DB. IDs are prefixed: 'guide_1', 'participant_2', 'admin_1'"""
    if '_' not in user_id:
        return None
    user_type, uid = user_id.split('_', 1)

    if user_type == 'guide':
        db_user = guides_dao.get_guide_by_id(uid)
        if db_user:
            return Guide(
                id=f"guide_{db_user['id']}",
                first_name=db_user['first_name'],
                last_name=db_user['last_name'],
                email=db_user['email'],
                password=db_user['password'],
                languages=db_user['languages'],
                profile_img_address=db_user['profile_img_address']
            )
    elif user_type == 'participant':
        db_user = participants_dao.get_participant_by_id(uid)
        if db_user:
            return Participant(
                id=f"participant_{db_user['id']}",
                first_name=db_user['first_name'],
                last_name=db_user['last_name'],
                email=db_user['email'],
                password=db_user['password']
            )
    elif user_type == 'admin':
        db_user = admins_dao.get_admin_by_id(uid)
        if db_user:
            return Admin(
                id=f"admin_{db_user['id']}",
                username=db_user['username'],
                password=db_user['password']
            )
    return None


def get_home_calendar_data(selected_date=None):
    """Fetch calendar tours for the specified week start date"""
    all_tours = tours_dao.get_all_tours()
    week_dates = get_week_dates(selected_date=selected_date)

    calendar = {day: [] for day in DAY_ORDER}
    for tour in all_tours:
        schedule = parse_schedule(tour['schedule'])
        guide = guides_dao.get_guide_by_id(tour['guide_id'])
        meetpoint = places_dao.get_place_by_id(tour['meetpoint_place_id'])

        for day, time in schedule.items():
            if time is None or day not in week_dates:
                continue
            day_date = week_dates[day]
            if day_date < date.today() or (day_date == date.today() and time < datetime.now().strftime("%H:%M")):
                continue
            rt = reserved_tours_dao.get_reserved_tour_by_tour_and_date(tour['id'], str(day_date))
            print(f"{tour['id']} {str(day_date)} => {rt}")
            tour_dict = dict(tour)
            for full_name, abbr in LANGUAGES.items():
                if tour_dict.get('language') == abbr:
                    tour_dict['language'] = full_name
                    break
            calendar[day].append({
                'tour': tour_dict,
                'date': day_date,
                'time': time,
                'reserved_tour': dict(rt) if rt else None,
                'guide_name': f"{guide['first_name']} {guide['last_name']}" if guide else 'Unknown',
                'meetpoint_name': meetpoint['name'] if meetpoint else 'Unknown'
            })
    return calendar, week_dates


def get_tour_detail_data(tour_id, participant_id=None):
    """Retrieve full tour details, stops, and dynamic booking fields for a participant"""
    tour = tours_dao.get_tour_by_id(tour_id)
    if not tour:
        return None

    tour = dict(tour)
    guide = guides_dao.get_guide_by_id(tour['guide_id'])
    meetpoint = places_dao.get_place_by_id(tour['meetpoint_place_id'])

    tvp_rows = tvp_dao.get_tour_visiting_places_by_tour(tour_id)
    stops = []
    for tvp in tvp_rows:
        place = places_dao.get_place_by_id(tvp['place_id'])
        if place:
            stops.append(place['name'])

    participant_reservations = []
    available_dates = []
    participant_booked_slots = set()
    # If a participant id is provided, collect any reservations that participant has for this tour
    if participant_id:
        reservations = reservations_dao.get_reservations_by_participant(participant_id)
        for res in reservations:
            rt = reserved_tours_dao.get_reserved_tour_by_id(res['reserved_tour_id'])
            if rt and rt['tour_id'] == tour_id:
                participant_booked_slots.add((rt['date'], rt['time']))
                participant_reservations.append({'reservation': dict(res), 'reserved_tour': dict(rt)})

    # Build list of available upcoming dates (only if capacity left)
    raw_dates = get_next_dates(tour['schedule'], weeks=4)
    for d in raw_dates:
        rt = reserved_tours_dao.get_reserved_tour_by_tour_and_date(tour_id, str(d['date']))
        if rt:
            available = tour['max_part_count'] - rt['expected_part_count']
        else:
            available = tour['max_part_count']
        if available > 0:
            is_booked = (str(d['date']), d['time']) in participant_booked_slots
            available_dates.append({**d, 'available': available, 'is_booked': is_booked})

    # Fetch all reserved tours and their reservations/participant details for admin views
    all_reserved_tours = []
    raw_rts = reserved_tours_dao.get_reserved_tours_by_tour(tour_id)
    for rt in raw_rts:
        rt_dict = dict(rt)
        res_list = reservations_dao.get_reservations_by_reserved_tour(rt['id'])
        enriched_res_list = []
        for res in res_list:
            res_dict = dict(res)
            part = participants_dao.get_participant_by_id(res['participant_id'])
            if part:
                res_dict['participant'] = dict(part)
            enriched_res_list.append(res_dict)
        rt_dict['reservations'] = enriched_res_list
        all_reserved_tours.append(rt_dict)

    all_reserved_tours.sort(key=lambda rt: (rt['date'], rt['time']))

    return {
        'tour': tour,
        'guide': dict(guide) if guide else None,
        'meetpoint_name': meetpoint['name'] if meetpoint else 'Unknown',
        'stops': stops,
        'participant_reservations': participant_reservations,
        'available_dates': available_dates,
        'all_reserved_tours': all_reserved_tours
    }


def book_tour_op(tour_id, participant_id, selected_date, selected_time, person_count, addit_1=None, addit_2=None, addit_3=None):
    """Handle booking logic, checking constraints and updating the DB"""
    tour = tours_dao.get_tour_by_id(tour_id)
    if not tour:
        return False, 'Tour not found.'

    # Prevent duplicate booking for the same participant/date for this tour
    existing_res = reservations_dao.get_reservations_by_participant(participant_id)
    for er in existing_res:
        ert = reserved_tours_dao.get_reserved_tour_by_id(er['reserved_tour_id'])
        if ert and ert['tour_id'] == tour_id and ert['date'] == selected_date:
            return False, f'You already have a reservation for this tour on {selected_date} at {ert["time"]}.'

    rt = reserved_tours_dao.get_reserved_tour_by_tour_and_date(tour_id, selected_date)
    if rt:
        available = tour['max_part_count'] - rt['expected_part_count']
        if person_count > available:
            return False, f'Not enough spots. Only {available} spot(s) left.'
        reserved_tours_dao.update_reserved_tour(rt['id'],
                                                expected_part_count=rt['expected_part_count'] + person_count)
        rt_id = rt['id']
    else:
        if person_count > tour['max_part_count']:
            return False, f'Cannot reserve {person_count} spots. Max is {tour["max_part_count"]}.'
        rt_id = reserved_tours_dao.create_reserved_tour(tour_id, selected_date, selected_time, person_count)

    if rt_id is None:
        return False, 'Booking failed. Please try again.'

    reservations_dao.create_reservation(participant_id, rt_id, person_count, addit_1, addit_2, addit_3)
    return True, 'Tour booked successfully!'


def cancel_reservation_op(reservation_id, participant_id):
    """Cancel reservation if owner and > 24 hours before start time"""
    res = reservations_dao.get_reservation_by_id(reservation_id)
    if not res:
        return False, 'Reservation not found.'

    if str(res['participant_id']) != str(participant_id):
        return False, 'You can only cancel your own reservations.'

    rt = reserved_tours_dao.get_reserved_tour_by_id(res['reserved_tour_id'])
    if not rt:
        return False, 'Reserved tour not found.'

    try:
        tour_dt = datetime.strptime(f"{rt['date']} {rt['time']}", "%Y-%m-%d %H:%M")
    except ValueError:
        return False, 'Invalid tour date/time format.'

    if datetime.now() >= tour_dt - timedelta(hours=24):
        return False, 'Cannot cancel within 24 hours of the tour start time.'

    reservations_dao.delete_reservation(reservation_id)

    # Decrease expected count
    new_count = rt['expected_part_count'] - res['person_count']
    reserved_tours_dao.update_reserved_tour(rt['id'], expected_part_count=max(new_count, 0))

    return True, 'Reservation cancelled successfully.'


def authenticate_user(credential, password):
    """Authenticate guide, participant, or admin. Returns (user_obj, welcome_message) or (None, error)"""

    # Try guides (by email)
    db_user = guides_dao.get_guide_by_email(credential)
    if db_user and check_password_hash(db_user['password'], password):
        user = Guide(
            id=f"guide_{db_user['id']}",
            first_name=db_user['first_name'],
            last_name=db_user['last_name'],
            email=db_user['email'],
            password=db_user['password'],
            languages=db_user['languages'],
            profile_img_address=db_user['profile_img_address']
        )
        return user, f"Welcome back, {db_user['first_name']}!"

    # Try participants (by email)
    db_user = participants_dao.get_participant_by_email(credential)
    if db_user and check_password_hash(db_user['password'], password):
        user = Participant(
            id=f"participant_{db_user['id']}",
            first_name=db_user['first_name'],
            last_name=db_user['last_name'],
            email=db_user['email'],
            password=db_user['password']
        )
        return user, f"Welcome back, {db_user['first_name']}!"

    # Try admin (by username)
    db_admin = admins_dao.get_admin_by_username(credential)
    if db_admin and check_password_hash(db_admin['password'], password):
        admin = Admin(
            id=f"admin_{db_admin['id']}",
            username=db_admin['username'],
            password=db_admin['password']
        )
        return admin, 'Welcome, Administrator!'

    return None, 'Invalid credentials. Please check your email/username and password.'


def signup_user(user_type, first_name, last_name, email, password, languages=None, profile_img_address=None):
    """Handle sign up business logic"""
    if guides_dao.get_guide_by_email(email) or participants_dao.get_participant_by_email(email):
        return False, 'This email address is already registered.'

    hashed = generate_password_hash(password)

    if user_type == 'guide':
        gid = guides_dao.create_guide(first_name, last_name, email, hashed, languages, profile_img_address)
        if gid:
            return True, 'Guide account created successfully! Please log in.'
        else:
            return False, 'Registration failed. Please try again.'

    elif user_type == 'participant':
        pid = participants_dao.create_participant(first_name, last_name, email, hashed)
        if pid:
            return True, 'Participant account created successfully! Please log in.'
        else:
            return False, 'Registration failed. Please try again.'

    return False, 'Invalid account type.'


def get_participant_profile_data(participant_id):
    """Gather enriched reservation details for the participant profile"""
    raw_reservations = reservations_dao.get_reservations_by_participant(participant_id)
    enriched = []
    now = datetime.now()
    for res in raw_reservations:
        rt = reserved_tours_dao.get_reserved_tour_by_id(res['reserved_tour_id'])
        if not rt:
            continue
        tour = tours_dao.get_tour_by_id(rt['tour_id'])
        meetpoint = None
        if tour:
            mp = places_dao.get_place_by_id(tour['meetpoint_place_id'])
            meetpoint = mp['name'] if mp else 'Unknown'
        try:
            tour_dt = datetime.strptime(f"{rt['date']} {rt['time']}", "%Y-%m-%d %H:%M")
            can_cancel = now < tour_dt - timedelta(hours=24)
            is_past = now > tour_dt
        except ValueError:
            can_cancel = False
            is_past = False
        enriched.append({
            'reservation': dict(res),
            'reserved_tour': dict(rt),
            'tour': dict(tour) if tour else None,
            'meetpoint_name': meetpoint,
            'can_cancel': can_cancel,
            'is_past': is_past
        })
    return enriched


def get_guide_profile_data(guide_id):
    """Gather enriched tour and reservation details for the guide profile"""
    raw_tours = tours_dao.get_tours_by_guide(guide_id)
    enriched_tours = []
    now = datetime.now()
    for tour in raw_tours:
        tour_dict = dict(tour)
        raw_rts = reserved_tours_dao.get_reserved_tours_by_tour(tour['id'])
        has_reservations = False
        enriched_rts = []
        for rt in raw_rts:
            rt_dict = dict(rt)
            res_list = reservations_dao.get_reservations_by_reserved_tour(rt['id'])
            if res_list:
                has_reservations = True
            try:
                tour_dt = datetime.strptime(f"{rt['date']} {rt['time']}", "%Y-%m-%d %H:%M")
                rt_dict['is_past'] = now > tour_dt
            except ValueError:
                rt_dict['is_past'] = False
            rt_dict['reportable'] = rt_dict['is_past'] and not rt['reported'] and bool(res_list)
            rt_dict['reservation_count'] = len(res_list) if res_list else 0
            enriched_rts.append(rt_dict)
        tour_dict['reserved_tours'] = enriched_rts
        tour_dict['has_reservations'] = has_reservations
        enriched_tours.append(tour_dict)
    return enriched_tours


def get_admin_profile_data():
    """Gather system statistics and all guide details for the admin dashboard"""
    all_guides = guides_dao.get_all_guides()
    all_participants = participants_dao.get_all_participants()
    all_tours = tours_dao.get_all_tours()
    all_reservations = reservations_dao.get_all_reservations()
    reverse_languages = {v: k for k, v in LANGUAGES.items()}

    # Reservations per language
    lang_stats = {}
    for tour in all_tours:
        lang_code = tour['language']
        lang = reverse_languages.get(lang_code, lang_code)
        rt_list = reserved_tours_dao.get_reserved_tours_by_tour(tour['id'])
        for rt in rt_list:
            res_list = reservations_dao.get_reservations_by_reserved_tour(rt['id'])
            lang_stats[lang] = lang_stats.get(lang, 0) + len(res_list)

    stats = {
        'total_guides': len(all_guides),
        'total_participants': len(all_participants),
        'total_tours': len(all_tours),
        'total_reservations': len(all_reservations),
        'lang_stats': lang_stats
    }

    # Enrich guides with their tours
    guides_with_tours = []
    for g in all_guides:
        g_dict = dict(g)
        g_dict['languages'] = [reverse_languages.get(code) for code in g_dict['languages'].split(';') if code]
        g_dict['tours'] = []
        for t in tours_dao.get_tours_by_guide(g['id']):
            t_dict = dict(t)
            t_dict['language'] = reverse_languages.get(t_dict['language'], t_dict['language'])
            g_dict['tours'].append(t_dict)
        guides_with_tours.append(g_dict)

    return stats, guides_with_tours


def create_tour_op(title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, photo_addresses, stops, guide_id):
    """Business logic for creating a new tour and its itinerary stops"""
    # Convert full language name to code
    language = LANGUAGES.get(language, language)

    # Resolve meeting point
    if new_meetpoint:
        place_id = places_dao.create_place(new_meetpoint)
    else:
        place_id = int(meetpoint_place_id)

    # Build schedule string
    schedule_parts = []
    for day in DAY_ORDER:
        if day in days:
            time_val = form_times.get(day, '').strip()
            schedule_parts.append(f"{day}_{time_val}")
        else:
            schedule_parts.append(f"{day}_X")
    schedule = ';'.join(schedule_parts)

    tour_id = tours_dao.create_tour(
        title, guide_id, schedule, place_id,
        int(duration), language, int(max_part_count), description,
        photo_addresses[0], photo_addresses[1], photo_addresses[2],
        photo_addresses[3], photo_addresses[4]
    )

    if not tour_id:
        return False, 'Failed to create tour. Please try again.', None

    # Add stops to itinerary
    for i, stop_name in enumerate(stops):
        stop_name = stop_name.strip()
        if not stop_name:
            continue
        place = places_dao.get_place_by_name(stop_name)
        if place:
            stop_place_id = place['id']
        else:
            stop_place_id = places_dao.create_place(stop_name)
        if stop_place_id:
            tvp_dao.add_place_to_tour(tour_id, stop_place_id, i + 1)

    return True, 'Tour created successfully!', tour_id


def edit_tour_op(tour_id, guide_id, title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, photo_addresses, stops=None):
    """Business logic for updating a tour. Validates if essential fields are locked."""
    tour = tours_dao.get_tour_by_id(tour_id)
    if not tour:
        return False, 'Tour not found.'

    if str(tour['guide_id']) != str(guide_id):
        return False, 'You can only edit your own tours.'

    has_reservations = False
    raw_rts = reserved_tours_dao.get_reserved_tours_by_tour(tour_id)
    for rt in raw_rts:
        res_list = reservations_dao.get_reservations_by_reserved_tour(rt['id'])
        if res_list:
            has_reservations = True
            break

    update_kwargs = {}
    if title:
        update_kwargs['title'] = title
    if description:
        update_kwargs['description'] = description

    if not has_reservations:
        if days:
            schedule_parts = []
            for day in DAY_ORDER:
                if day in days:
                    time_val = form_times.get(day, '').strip()
                    schedule_parts.append(f"{day}_{time_val}" if time_val else f"{day}_X")
                else:
                    schedule_parts.append(f"{day}_X")
            update_kwargs['schedule'] = ';'.join(schedule_parts)

        if new_meetpoint:
            update_kwargs['meetpoint_place_id'] = places_dao.create_place(new_meetpoint)
        elif meetpoint_place_id:
            update_kwargs['meetpoint_place_id'] = int(meetpoint_place_id)

        if duration:
            update_kwargs['duration'] = int(duration)
        if language:
            # convert full language name to stored code if needed
            update_kwargs['language'] = LANGUAGES.get(language, language)
        if max_part_count:
            update_kwargs['max_part_count'] = int(max_part_count)

    for i in range(1, 6):
        addr = photo_addresses[i-1]
        if addr:
            update_kwargs[f'photo_{i}_address'] = addr
    tours_dao.update_tour(tour_id, **update_kwargs)

    # Update itinerary stops if provided and no reservations exist
    if not has_reservations and stops is not None:
        # Remove existing visiting places and add the new list
        tvp_dao.delete_places_for_tour(tour_id)
        for i, stop_name in enumerate(stops):
            stop_name = stop_name.strip()
            if not stop_name:
                continue
            place = places_dao.get_place_by_name(stop_name)
            if place:
                stop_place_id = place['id']
            else:
                stop_place_id = places_dao.create_place(stop_name)
            if stop_place_id:
                tvp_dao.add_place_to_tour(tour_id, stop_place_id, i + 1)
    return True, 'Tour updated successfully!'


def report_tour_op(reserved_tour_id, guide_id, actual_count, proof_img_address=None):
    """Business logic for reporting a completed tour"""
    rt = reserved_tours_dao.get_reserved_tour_by_id(reserved_tour_id)
    if not rt:
        return False, 'Reserved tour not found.'

    tour = tours_dao.get_tour_by_id(rt['tour_id'])
    if not tour or str(tour['guide_id']) != str(guide_id):
        return False, 'You can only report your own tours.'

    final_proof_img = proof_img_address if proof_img_address else rt['proof_img_address']
    reserved_tours_dao.update_reserved_tour(
        reserved_tour_id,
        actual_part_count=int(actual_count),
        proof_img_address=final_proof_img,
        reported=1
    )
    return True, 'Tour reported successfully!'


def get_database_dump():
    """Retrieve all rows from all database tables as a dictionary for debugging"""
    import sqlite3
    tables = ['Guides', 'Participants', 'Admins', 'Tours', 'Places', 'Reserved_Tours', 'Reservations', 'Tour_Visiting_Places']
    dump = {}
    try:
        conn = sqlite3.connect("database/space_tours.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                dump[table] = [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                dump[table] = f"Error: {e}"
        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        dump['error'] = str(e)
    return dump
