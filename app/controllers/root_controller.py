import os
import flask
from app.controllers import BaseController
from app.template import TemplateEngine

class RootController(BaseController):
    @classmethod
    def index(cls, app_version: dict):
        user = super().get_auth_user()
        new_league = flask.request.args.get("new_league")
        return TemplateEngine.render("index", {
                "version": app_version, 
                "dev_environment": cls.DEV_ENVIRONMENT, 
                "user": user, 
                "new_league": new_league
            })