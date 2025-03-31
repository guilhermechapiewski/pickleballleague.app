import os
import flask
import logging
from app.controllers import BaseController
from app.models import Series, SeriesShortLink
from app.repositories import SeriesRepository, LeagueRepository, UserRepository, SeriesShortLinkRepository
from app.template import TemplateEngine

logger = logging.getLogger(__name__)

class SeriesController(BaseController):
    @classmethod
    def create_series(cls):
        user = super().get_auth_user()
        series_name = flask.request.form.get("series_name")
        series_selected_leagues = flask.request.form.get("series_selected_leagues")
        logger.info(f"Creating series name=[{series_name}] for leagues=[{series_selected_leagues}]")
        
        series = Series(name=series_name)
        series.set_owner(user)
        for league_id in series_selected_leagues.split(","):
            league = LeagueRepository.get_league(league_id)
            series.add_league(league)
        SeriesRepository.save_series(series)

        user = UserRepository.get_user(user.email)
        user.add_series(series.id)
        UserRepository.save_user(user)

        return flask.redirect("/profile")
    
    @classmethod
    def get_series(cls, series_id: str):
        user = super().get_auth_user()
        try:
            # first check if a short link exists to get the actual league_id
            short_link = SeriesShortLinkRepository.get_short_link(series_id)
            if short_link:
                series_id = short_link.destination_link
            
            # retrieve series
            series = SeriesRepository.get_series(series_id)
            return TemplateEngine.render(f"series", {
                "series": series,
                "user": user,
                "dev_environment": cls.DEV_ENVIRONMENT,
                "domain_name": flask.request.host
            })
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.exception(e)
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Series not found",
                "message": "The series you are looking for does not exist. Please check the URL and try again."
            })
    
    @classmethod
    def delete_series(cls, series_id: str):
        user = super().get_auth_user()
        series = SeriesRepository.get_series(series_id)
        logger.info(f"Deleting series: {series.to_object()}")

        if series:
            if series.owner and series.owner.email == user.email:
                SeriesRepository.delete_series(series_id)
                user = UserRepository.get_user(user.email)
                user.remove_series(series_id)
                UserRepository.save_user(user)
                return flask.redirect("/profile")
            else:
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
                    "user": user,
                    "title": "Error: Permission denied",
                    "message": "You are not the owner of this series."
                })
        else:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Series not found",
                "message": "The series you are trying to delete does not exist."
            })
    
    @classmethod
    def save_series(cls):
        user = super().get_auth_user()
        series_id = flask.request.form.get("series_id")
        
        # first check if the short link exists
        short_link = SeriesShortLinkRepository.get_short_link(series_id)
        if short_link:
            series_id = short_link.destination_link
        
        series = SeriesRepository.get_series(series_id)

        # check if the short link needs to be updated
        update_series_id = flask.request.form.get("update_series_id")
        new_series_id = flask.request.form.get("new_series_id")
        if update_series_id and new_series_id and update_series_id == "1":
            # check if the new short link already exists
            short_link = SeriesShortLinkRepository.get_short_link(new_series_id)
            if short_link:
                logger.error(f"Short link already exists: {new_series_id}")
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
                    "user": user,
                    "title": "Error: Short link already exists",
                    "message": "The short link you chose already exists. Please check the URL and try again.",
                    "action_name": "Back to series",
                    "action_url": f"/series/{series_id}"
                })
            else:
                short_link = SeriesShortLink(new_series_id, series.id)
                SeriesShortLinkRepository.save_short_link(short_link)
                series.set_short_link(new_series_id)
        
        # now update the series name
        update_series_name = flask.request.form.get("update_series_name")
        new_series_name = flask.request.form.get("new_series_name")
        if new_series_name and update_series_name and update_series_name == "1" and new_series_name != "":
            series.name = new_series_name
        
        # now update the series contributors
        update_contributors = flask.request.form.get("update_contributors")
        new_contributor_email = flask.request.form.get("new_contributor_email")
        if update_contributors and update_contributors == "1" and new_contributor_email and new_contributor_email != "":
            contributor = UserRepository.get_user(new_contributor_email)
            if contributor:
                series.add_contributor(contributor)
                contributor.add_series(series.id)
                UserRepository.save_user(contributor)
            else:
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
                    "user": user,
                    "title": "Error: User not found",
                    "message": f"The contributor you are trying to add (<i>{new_contributor_email}</i>) was not found in the user database.",
                    "action_name": "Back to series",
                    "action_url": f"/series/{series_id}"
                })
        
        SeriesRepository.save_series(series)
        return flask.redirect(f"/series/{series.id}" if not series.short_link else f"/series/{series.short_link}")

    @classmethod
    def remove_league_from_series(cls, series_id: str, league_id: str):
        user = super().get_auth_user()
        series = SeriesRepository.get_series(series_id)
        league = LeagueRepository.get_league(league_id)
        
        series.remove_league(league_id)
        SeriesRepository.save_series(series)

        user.remove_league(league_id)
        UserRepository.save_user(user)

        return flask.redirect(f"/series/{series_id}")
    
    @classmethod
    def add_league_to_series(cls, series_id: str):
        user = super().get_auth_user()
        series = SeriesRepository.get_series(series_id)
        league_id = flask.request.form.get("league_id")
        league = LeagueRepository.get_league(league_id)
        
        if not league:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: League not found",
                "message": "The league you are trying to add does not exist."
            })
        
        if series.owner and series.owner.email == user.email:
            series.add_league(league)
            SeriesRepository.save_series(series)
            return flask.redirect(f"/series/{series_id}")
        else:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Permission denied",
                "message": "You are not the owner of this series."
            })