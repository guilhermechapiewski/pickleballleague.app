import os
import flask
import logging
from app.models import User
from app.repositories import UserRepository, LeagueRepository, SeriesRepository
from app.controllers import BaseController
from app.template import TemplateEngine

logger = logging.getLogger(__name__)

class UserController(BaseController):
    @classmethod
    def sign_in(cls):
        user = super().get_auth_user()

        if not user:
            user_google_id = flask.request.form.get("user_google_id")
            user_email = flask.request.form.get("user_email")
            logger.info(f"User email+id: [{user_email}|{user_google_id}]")
            # if user_google_id and email are not empty, it means they signed in with Google and we need to get the user from the database
            if user_email:
                # get from database
                user = UserRepository.get_user(user_email)
                # if no user_id is found, it means they are a new user
                if not user:
                    user = User(email=user_email, google_id=user_google_id)
                    UserRepository.save_user(user)
            
            # Set session variables for the authenticated user
            if user:
                flask.session['user_id'] = user.id
                flask.session['user_email'] = user.email
                flask.session['user_google_id'] = user.google_id
        
        return flask.redirect(flask.request.referrer or "/")
    
    @classmethod
    def sign_out(cls):
        flask.session.clear()
        return flask.redirect("/")

    @classmethod
    def get_profile(cls):
        user = super().get_auth_user()

        if not user:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Not logged in",
                "message": "Please sign in to view your profile."
            })
        
        # get full user object from database
        user = UserRepository.get_user(user.email)

        leagues = []
        for league_id in user.league_ids:
            league = LeagueRepository.get_league(league_id)
            leagues.append(league)
        
        series = []
        for series_id in user.series_ids:
            a_series = SeriesRepository.get_series(series_id)
            series.append(a_series)

        logger.info(f"User: {user.to_object()}")
        return TemplateEngine.render("profile", {
            "dev_environment": cls.DEV_ENVIRONMENT, 
            "user": user, 
            "leagues": leagues,
            "series": series,
            "domain_name": flask.request.host
        })