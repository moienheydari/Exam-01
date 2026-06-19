from flask_login import UserMixin

class User(UserMixin):
    """Base user class for authentication"""
    def __init__(self, id, first_name, last_name, email, password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class Participant(User):
    """Participant model"""
    def __init__(self, id, first_name, last_name, email, password):
        super().__init__(id, first_name, last_name, email, password)
        self.user_type = "participant"


class Guide(User):
    """Tour guide model"""
    def __init__(self, id, first_name, last_name, email, password, languages, profile_img_address):
        super().__init__(id, first_name, last_name, email, password)
        self.languages = languages
        self.user_type = "guide"
        self.profile_img_address = profile_img_address


class Admin(UserMixin):
    """Admin user model"""
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.user_type = "admin"
