import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Monkeypatch sqlite3.connect to ensure the absolute path is always used
_original_connect = sqlite3.connect

def _patched_connect(database, *args, **kwargs):
    if database == "database/space_tours.db":
        database = os.path.join(BASE_DIR, "database", "space_tours.db")
    return _original_connect(database, *args, **kwargs)

sqlite3.connect = _patched_connect

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import ops.ops as ops
import ops.validators as validators
from datetime import date, datetime
import os

import database.reserved_tours_dao as reserved_tours_dao
import database.reservations_dao as reservations_dao
import database.tours_dao as tours_dao
import database.places_dao as places_dao
import database.tour_visiting_places_dao as tvp_dao

LANGUAGES = {'English': 'eng', 'Italian': 'it', 'Spanish': 'sp', 'Portuguese': 'por', 'German': 'ger'}

# --- App setup ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret Key for Space Tours"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# --- User loader ---

@login_manager.user_loader
def load_user(user_id):
    """Load user using prefixes via the business operations layer"""
    return ops.get_user_by_prefixed_id(user_id)


# --- Routes ---

@app.route('/')
def home():
    """Homepage: weekly calendar of tours. Accepts ?start=YYYY-MM-DD for any custom week."""
    today = date.today()

    # Read custom start date; reject past dates; fall back to current-week Monday
    start_str = request.args.get('start', None)
    selected_date = None
    if start_str:
        try:
            parsed = date.fromisoformat(start_str)
            if parsed >= today:        # only allow today or future
                selected_date = parsed
        except ValueError:
            selected_date = None

    calendar, week_dates = ops.get_home_calendar_data(selected_date=selected_date)

    return render_template('index.html',
                           calendar=calendar,
                           day_order=ops.DAY_ORDER,
                           week_dates=week_dates,
                           languages=ops.LANGUAGES.keys(),
                           selected_date=selected_date,
                           today=today)


@app.route('/tour/<int:tour_id>')
def tour_detail(tour_id):
    """Full tour page: details, photos, stops, booking form for participants"""
    participant_id = None
    if current_user.is_authenticated and current_user.user_type == 'participant':
        _, pid = current_user.id.split('_', 1)
        participant_id = pid

    # Accept optional preselected date/time from the clicked tour card
    initial_selected_date = request.args.get('selected_date')
    initial_selected_time = request.args.get('selected_time')

    data = ops.get_tour_detail_data(tour_id, participant_id=participant_id)
    if not data:
        flash('Tour not found.', 'warning')
        return redirect(url_for('home'))

    reverse_languages = {v: k for k, v in LANGUAGES.items()}
    if data['tour'].get('language') in reverse_languages:
        data['tour']['language'] = reverse_languages[data['tour']['language']]

    return render_template('tour_booking.html',
                           tour=data['tour'],
                           guide=data['guide'],
                           meetpoint=data['meetpoint_name'],
                           stops=data['stops'],
                           participant_reservations=data.get('participant_reservations', []),
                           available_dates=data['available_dates'],
                           initial_selected_date=initial_selected_date,
                           initial_selected_time=initial_selected_time,
                           all_reserved_tours=data.get('all_reserved_tours', []))


@app.route('/book/<int:tour_id>', methods=['POST'])
@login_required
def book_tour(tour_id):
    """Handle tour booking by a participant"""
    if current_user.user_type != 'participant':
        flash('Only participants can book tours.', 'danger')
        return redirect(url_for('tour_detail', tour_id=tour_id))

    _, pid = current_user.id.split('_', 1)
    selected_date = request.form.get('selected_date')
    selected_time = request.form.get('selected_time')
    person_count = int(request.form.get('person_count', 1))
    addit_1 = request.form.get('addit_person_1', '').strip() or None
    addit_2 = request.form.get('addit_person_2', '').strip() or None
    addit_3 = request.form.get('addit_person_3', '').strip() or None
    current_tour = tours_dao.get_tour_by_id(tour_id)
    is_valid, err_msg = validators.validate_booking(
        selected_date, selected_time, person_count, addit_1, addit_2, addit_3, current_tour, pid
    )
    if not is_valid:
        flash(err_msg, 'danger')
        return redirect(url_for('tour_detail', tour_id=tour_id))

    success, message = ops.book_tour_op(
        tour_id=tour_id,
        participant_id=pid,
        selected_date=selected_date,
        selected_time=selected_time,
        person_count=person_count,
        addit_1=addit_1,
        addit_2=addit_2,
        addit_3=addit_3
    )

    flash(message, 'success' if success else 'danger')
    if success:
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('tour_detail', tour_id=tour_id))


@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """Cancel a reservation (participant only, must be >24h before start)"""
    is_valid, err_msg = validators.validate_cancellation(reservation_id, current_user.user_type)
    if not is_valid:
        flash(err_msg, 'danger')
        return redirect(url_for('profile'))

    _, pid = current_user.id.split('_', 1)
    success, message = ops.cancel_reservation_op(reservation_id, pid)

    flash(message, 'success' if success else 'danger')
    return redirect(url_for('profile'))


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    next_url = request.args.get('next')
    return render_template('login.html', next=next_url)


@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Log in: check Guides → Participants → Admins in order"""
    credential = request.form.get('txt_email', '').strip()
    password = request.form.get('txt_password', '').strip()
    next_url = request.args.get('next')

    is_valid, err_msg = validators.validate_authentication(credential, password)
    if not is_valid:
        flash(err_msg, 'danger')
        return redirect(url_for('login', next=next_url))

    user, message = ops.authenticate_user(credential, password)
    if user:
        login_user(user)
        flash(message, 'success')
        if user.user_type == 'admin':
            return redirect(url_for('profile'))
        if user.user_type == 'guide':
            return redirect(url_for('profile'))
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect(url_for('home'))
    else:
        flash(message, 'danger')
        return redirect(url_for('login', next=next_url))


@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('register.html', languages=ops.LANGUAGES.keys())


@app.route('/signup', methods=['POST'])
def signup():
    """Handle registration form for guides and participants"""
    user_type = request.form.get('user_type')
    first_name = request.form.get('txt_first_name', '').strip()
    last_name = request.form.get('txt_last_name', '').strip()
    email = request.form.get('txt_email', '').strip()
    password = request.form.get('txt_password', '').strip()

    languages_list = request.form.getlist('languages')
    profile_img = request.files.get('profile_img')

    is_valid, err_msg = validators.validate_signup(
        user_type, first_name, last_name, email, password, languages_list, profile_img
    )
    if not is_valid:
        flash(err_msg, 'danger')
        return redirect(url_for('register'))

    profile_img_address = None
    if user_type == 'guide':
        profile_img = request.files.get('profile_img')
        if profile_img and profile_img.filename:
            ext = profile_img.filename.rsplit('.', 1)[-1].lower()
            filename = f"{int(datetime.now().timestamp())}.{ext}"
            folder_path = os.path.join(BASE_DIR, 'static', 'images', 'profile_imgs')
            os.makedirs(folder_path, exist_ok=True)
            save_path = os.path.join(folder_path, filename)
            profile_img.save(save_path)
            profile_img_address = f"images/profile_imgs/{filename}"

    languages_list = request.form.getlist('languages')
    languages_mapped = [LANGUAGES.get(lang, lang) for lang in languages_list]
    languages_str = ';'.join(languages_mapped) if languages_list else None

    success, message = ops.signup_user(
        user_type=user_type,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        languages=languages_str,
        profile_img_address=profile_img_address
    )

    flash(message, 'success' if success else 'danger')
    if success:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register'))


@app.route('/profile')
@login_required
def profile():
    """Profile page: different content per user type"""
    if current_user.user_type == 'participant':
        _, pid = current_user.id.split('_', 1)
        reservations = ops.get_participant_profile_data(pid)
        # Sort reservations chronologically by date and time
        reservations.sort(key=lambda r: (r['reserved_tour']['date'], r['reserved_tour']['time']))
        return render_template('profile.html', reservations=reservations)

    elif current_user.user_type == 'guide':
        _, gid = current_user.id.split('_', 1)
        tours = ops.get_guide_profile_data(gid)
        # Sort by Time
        for t in tours:
            t['reserved_tours'].sort(key=lambda rt: (rt['date'], rt['time']))
        # Sort by Date
        tours.sort(key=lambda t: min((rt['date'] for rt in t['reserved_tours']), default='9999-12-31'))
        # Convert language codes to English names for the guide
        reverse_languages = {v: k for k, v in LANGUAGES.items()}
        guide_languages = [reverse_languages.get(code) for code in current_user.languages.split(';') if code]
        return render_template('profile.html', tours=tours, languages=guide_languages)

    elif current_user.user_type == 'admin':
        stats, guides_with_tours = ops.get_admin_profile_data()
        return render_template('profile.html', stats=stats, guides=guides_with_tours)

    return redirect(url_for('home'))


@app.route('/create_tour', methods=['GET', 'POST'])
@login_required
def create_tour():
    """Create a new tour (guide only)"""
    if current_user.user_type != 'guide':
        flash('Only guides can create tours.', 'danger')
        return redirect(url_for('home'))

    _, gid = current_user.id.split('_', 1)
    # Convert language codes to English names
    reverse_languages = {v: k for k, v in LANGUAGES.items()}
    guide_languages = [reverse_languages.get(code) for code in current_user.languages.split(';') if code]
    all_places = places_dao.get_all_places()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration', '').strip()
        language = request.form.get('language', '').strip()
        max_part_count = request.form.get('max_part_count', '').strip()
        meetpoint_place_id = request.form.get('meetpoint_place_id', '').strip()
        new_meetpoint = request.form.get('new_meetpoint', '').strip()
        days = request.form.getlist('schedule_days')

        # Read times dictionary from form
        form_times = {day: request.form.get(f'time_{day}', '').strip() for day in ops.DAY_ORDER}
        stops = request.form.getlist('stops')

        # Validate using validators module
        photo_files = {f'photo_{i}': request.files.get(f'photo_{i}') for i in range(1, 6)}
        is_valid, err_msg = validators.validate_create_tour(
            title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, stops, guide_languages, photo_files
        )
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('create_tour.html', languages=guide_languages, places=all_places, day_order=ops.DAY_ORDER)

        # Handle 5 photo uploads now that validation has succeeded
        photo_addresses = []
        for i in range(1, 6):
            photo = request.files.get(f'photo_{i}')
            if photo and photo.filename:
                ext = photo.filename.rsplit('.', 1)[-1].lower()
                filename = f"tour_{int(datetime.now().timestamp())}_{i}.{ext}"
                folder_path = os.path.join(BASE_DIR, 'static', 'images', 'tour_imgs')
                os.makedirs(folder_path, exist_ok=True)
                save_path = os.path.join(folder_path, filename)
                photo.save(save_path)
                photo_addresses.append(f"images/tour_imgs/{filename}")
            else:
                photo_addresses.append(None)

        success, message, tour_id = ops.create_tour_op(
            title=title,
            description=description,
            duration=duration,
            language=language,
            max_part_count=max_part_count,
            meetpoint_place_id=meetpoint_place_id,
            new_meetpoint=new_meetpoint,
            days=days,
            form_times=form_times,
            photo_addresses=photo_addresses,
            stops=stops,
            guide_id=gid
        )

        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('profile'))
        else:
            return render_template('create_tour.html', languages=guide_languages, places=all_places, day_order=ops.DAY_ORDER)

    return render_template('create_tour.html', languages=guide_languages, places=all_places, day_order=ops.DAY_ORDER)


@app.route('/edit_tour/<int:tour_id>', methods=['GET', 'POST'])
@login_required
def edit_tour(tour_id):
    """Edit a tour (guide only). Essential fields locked once any reservation exists."""
    if current_user.user_type != 'guide':
        flash('Only guides can edit tours.', 'danger')
        return redirect(url_for('home'))

    _, gid = current_user.id.split('_', 1)
    
    # We still need places/tour information for the GET request display

    tour = tours_dao.get_tour_by_id(tour_id)
    if not tour:
        flash('Tour not found.', 'danger')
        return redirect(url_for('profile'))

    tour_dict = dict(tour)
    schedule = ops.parse_schedule(tour_dict['schedule'])

    if str(tour['guide_id']) != gid:
        flash('You can only edit your own tours.', 'danger')
        return redirect(url_for('profile'))

    # Determine if essential fields are locked
    has_reservations = False
    raw_rts = reserved_tours_dao.get_reserved_tours_by_tour(tour_id)
    for rt in raw_rts:
        res_list = reservations_dao.get_reservations_by_reserved_tour(rt['id'])
        if res_list:
            has_reservations = True
            break

    # Convert language codes to English names
    reverse_languages = {v: k for k, v in LANGUAGES.items()}
    guide_languages = [reverse_languages.get(code) for code in current_user.languages.split(';') if code]
    all_places = places_dao.get_all_places()

    # Current stops
    tvp_rows = tvp_dao.get_tour_visiting_places_by_tour(tour_id)
    current_stops = []
    for tvp in tvp_rows:
        place = places_dao.get_place_by_id(tvp['place_id'])
        if place:
            current_stops.append(place['name'])

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration', '').strip()
        language = request.form.get('language', '').strip()
        max_part_count = request.form.get('max_part_count', '').strip()
        meetpoint_place_id = request.form.get('meetpoint_place_id', '').strip()
        new_meetpoint = request.form.get('new_meetpoint', '').strip()
        days = request.form.getlist('schedule_days')

        form_times = {day: request.form.get(f'time_{day}', '').strip() for day in ops.DAY_ORDER}
        stops = request.form.getlist('stops')

        # Validate using validators module
        photo_files = {f'photo_{i}': request.files.get(f'photo_{i}') for i in range(1, 6)}
        is_valid, err_msg = validators.validate_edit_tour(
            title, description, duration, language, max_part_count, meetpoint_place_id, new_meetpoint, days, form_times, stops, guide_languages, photo_files, has_reservations
        )
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('edit_tour.html', tour=tour_dict, schedule=schedule, has_reservations=has_reservations, places=all_places, guide_languages=guide_languages, current_stops=current_stops, day_order=ops.DAY_ORDER)

        # Photo updates (only if validation succeeded)
        photo_addresses = []
        for i in range(1, 6):
            photo = request.files.get(f'photo_{i}')
            if photo and photo.filename:
                ext = photo.filename.rsplit('.', 1)[-1].lower()
                filename = f"tour_{int(datetime.now().timestamp())}_{i}.{ext}"
                folder_path = os.path.join(BASE_DIR, 'static', 'images', 'tour_imgs')
                os.makedirs(folder_path, exist_ok=True)
                save_path = os.path.join(folder_path, filename)
                photo.save(save_path)
                photo_addresses.append(f"images/tour_imgs/{filename}")
            else:
                photo_addresses.append(None)

        success, message = ops.edit_tour_op(
            tour_id=tour_id,
            guide_id=gid,
            title=title,
            description=description,
            duration=duration,
            language=language,
            max_part_count=max_part_count,
            meetpoint_place_id=meetpoint_place_id,
            new_meetpoint=new_meetpoint,
            days=days,
            form_times=form_times,
            photo_addresses=photo_addresses,
            stops=stops
        )

        flash(message, 'success' if success else 'danger')
        return redirect(url_for('profile'))

    return render_template('edit_tour.html',
                           tour=tour_dict,
                           schedule=schedule,
                           has_reservations=has_reservations,
                           places=all_places,
                           guide_languages=guide_languages,
                           current_stops=current_stops,
                           day_order=ops.DAY_ORDER)


@app.route('/report_tour/<int:reserved_tour_id>', methods=['GET', 'POST'])
@login_required
def report_tour(reserved_tour_id):
    """Guide reports actual attendance for a past tour date"""
    if current_user.user_type != 'guide':
        flash('Only guides can report tours.', 'danger')
        return redirect(url_for('home'))

    # We need to fetch information for the display of GET requests
    rt = reserved_tours_dao.get_reserved_tour_by_id(reserved_tour_id)
    if not rt:
        flash('Reserved tour not found.', 'danger')
        return redirect(url_for('profile'))

    tour = tours_dao.get_tour_by_id(rt['tour_id'])
    _, gid = current_user.id.split('_', 1)

    if not tour or str(tour['guide_id']) != gid:
        flash('You can only report your own tours.', 'danger')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        actual_count = request.form.get('actual_part_count', '').strip()

        # Validate using validators module
        proof_img = request.files.get('proof_img')
        is_valid, err_msg = validators.validate_report_tour(
            actual_count, rt['expected_part_count'], rt['date'], rt['time'], proof_img
        )
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('report_tour.html', rt=dict(rt), tour=dict(tour))

        # Save the photo and compile proof_img_address now that validation succeeded
        ext = proof_img.filename.rsplit('.', 1)[-1].lower()
        filename = f"proof_{int(datetime.now().timestamp())}.{ext}"
        folder_path = os.path.join(BASE_DIR, 'static', 'images', 'proof_imgs')
        os.makedirs(folder_path, exist_ok=True)
        save_path = os.path.join(folder_path, filename)
        proof_img.save(save_path)
        proof_img_address = f"images/proof_imgs/{filename}"

        success, message = ops.report_tour_op(
            reserved_tour_id=reserved_tour_id,
            guide_id=gid,
            actual_count=actual_count,
            proof_img_address=proof_img_address
        )

        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('profile'))
        else:
            return render_template('report_tour.html', rt=dict(rt), tour=dict(tour))

    return render_template('report_tour.html', rt=dict(rt), tour=dict(tour))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
