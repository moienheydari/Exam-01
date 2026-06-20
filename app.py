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
app.config["SECRET_KEY"] = "Secret Key for Space Tours"
