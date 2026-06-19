from flask import Flask, render_template, request, redirect, url_for, flash

from flask_login import LoginManager, login_user, logout_user, login_required
## EDIT
from database.models import User 

## EDIT
import database.users_dao as users_dao, database.tutors_dao as tutors_dao
from datetime import date, datetime

from werkzeug.security import generate_password_hash, check_password_hash

from PIL import Image

## EDIT
PROFILE_IMG_HEIGHT = 130


app = Flask(__name__)
## EDIT
app.config["SECRET_KEY"] = "Secret Key for Space Tours"

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def home():
## EDIT
    return render_template("index.html")


@app.route("/myhistory")
@login_required
def history():
    return render_template("history.html")


@app.route("/tutors")
def tutors():
    db_tutors = tutors_dao.get_tutors()

    return render_template("tutors.html", ptutors=tutors_list)


@app.route("/new_tutor")
def new_tutor():
    return render_template("new_tutor.html")


@app.route("/register_tutor", methods=["POST"])
def register_tutor():
    email = request.form.get("txt_email")
    bio = request.form.get("txt_bio")

    users_dao.get_id_by_email(p_email=email)

    return redirect(url_for("home"))


@app.route("/single_tutor/<int:id_tutor>")
def single_tutor(id_tutor):
    selected_tutor = tutors_list[id_tutor]
    parent_link = "tutors"
    return render_template("tutor.html", ptutor=selected_tutor, plink=parent_link)


@app.route("/signup")
def signup():
    return render_template("registration.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("txt_name")
    surname = request.form.get("txt_surname")
    email = request.form.get("txt_email")
    password = generate_password_hash(request.form.get("txt_password"))

    subjects = request.form.getlist("subjects")

    print(subjects)

    img_name = ""

    profile_img = request.files["profile_img"]
    if profile_img:
        
        img = Image.open(profile_img)

        width, height = img.size

        new_width = PROFILE_IMG_HEIGHT * width / height

        size = new_width, PROFILE_IMG_HEIGHT
        img.thumbnail(size, Image.Resampling.LANCZOS)

        left = new_width / 2 - PROFILE_IMG_HEIGHT / 2
        top = 0
        right = new_width / 2 + PROFILE_IMG_HEIGHT / 2
        bottom = PROFILE_IMG_HEIGHT

        img = img.crop((left, top, right, bottom))

        secs = int(datetime.now().timestamp())

        ext = profile_img.filename.split(".")[-1]

        img_name = str(secs) + "." + ext
        img.save("static/images/profile_imgs/" + img_name)

    users_dao.new_user(name, surname, email, password, "images/profile_imgs/" + img_name)

    return redirect(url_for("home"))


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    form_user = request.form.to_dict()

    db_user = users_dao.get_user_by_email(form_user["txt_email"])

    if not db_user:
        # print("The user does not exist")
        flash("The user does not exist", "danger")
        return redirect(url_for("home"))
    elif not check_password_hash(db_user["password"], form_user["txt_password"]):
        # print("The password is wrong")
        flash("The password is wrong", "danger")
        return redirect(url_for("home"))
    else:
        new = User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            email=db_user["email"],
            password=db_user["password"],
            profile_img=db_user["profile_img"],
        )

        result = login_user(new)
        flash("Welcome back! " + db_user["name"] + "!", "success")
        # print(result)

    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    db_user = users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            email=db_user["email"],
            password=db_user["password"],
            profile_img=db_user["profile_img"],
        )
    else:
        user = None

    return user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
