import os
import flask
from app.models import User

class BaseController:
    DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"

    @classmethod
    def get_auth_user(cls) -> User:
        user = None
        # Check if user is already authenticated
        if flask.session.get("user_id") and flask.session.get("user_google_id") and flask.session.get("user_email"):
            user = User()
            user.id = flask.session.get("user_id")
            user.google_id = flask.session.get("user_google_id")
            user.email = flask.session.get("user_email")
        return user