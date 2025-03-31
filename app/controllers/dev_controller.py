import os
import flask
from app.controllers import BaseController
from app.models import League, ScoringSystem, Series, User
from app.repositories import LeagueRepository, SeriesRepository, UserRepository, DevLocalDB
from app.template import TemplateEngine

class DevController(BaseController):
    @classmethod
    def load_test_data(cls):
        if not cls.DEV_ENVIRONMENT:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error",
                "message": "This feature is only available in the development environment."
            })
        
        user = super().get_auth_user()
        if not user:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error",
                "message": "Please sign in to load test data."
            })
        else:
            user = UserRepository.get_user(user.email)
        
        league = League(name="League with 4 players, 3 rounds", player_names="GC, Juliano, Fariba, Galina")
        league.generate_schedule(rounds=3)
        league.set_scoring_system(ScoringSystem.SCORE)
        league.set_owner(user)
        LeagueRepository.save_league(league)
        user.add_league(league.id)
        
        league = League(name="League with 5 players, 5 rounds", player_names="GC, Juliano, Fariba, Galina, Aline")
        league.generate_schedule(rounds=5)
        league.set_scoring_system(ScoringSystem.SCORE)
        league.set_owner(user)
        LeagueRepository.save_league(league)
        user.add_league(league.id)
        
        league_in_series1 = League(name="League with 6 players, 5 rounds", player_names="GC, Juliano, Fariba, Galina, Aline, Irina")
        league_in_series1.generate_schedule(rounds=5)
        league_in_series1.set_scoring_system(ScoringSystem.SCORE)
        league_in_series1.set_owner(user)
        LeagueRepository.save_league(league_in_series1)
        user.add_league(league_in_series1.id)

        league_in_series2 = League(name="League with 9 players, 7 rounds", player_names="GC, Juliano, Fariba, Galina, Aline, Irina, Regina, Lana, Raquel")
        league_in_series2.generate_schedule(rounds=7)
        league_in_series2.set_scoring_system(ScoringSystem.SCORE)
        league_in_series2.set_owner(user)
        LeagueRepository.save_league(league_in_series2)
        user.add_league(league_in_series2.id)

        series = Series(name="Series with 2 leagues")
        series.add_league(league_in_series1)
        series.add_league(league_in_series2)
        series.set_owner(user)
        SeriesRepository.save_series(series)
        user.add_series(series.id)
        
        # a very big league belonging with a contributor
        other_user = User(email="other@example.com")

        league = League(name="W/L League with 11 players, 10 rounds", player_names="GC, Juliano, Fariba, Galina, Aline, Irina, Regina, Lana, Bruno, Igor, Yuri")
        league.generate_schedule(rounds=7)
        league.set_scoring_system(ScoringSystem.W_L)
        league.set_owner(user)
        league.add_contributor(other_user)
        LeagueRepository.save_league(league)
        user.add_league(league.id)

        other_league = League(name="League with 4 players, 3 rounds (other user owns it)", player_names="GC, Juliano, Fariba, Galina")
        other_league.generate_schedule(rounds=3)
        other_league.set_scoring_system(ScoringSystem.SCORE)
        other_league.set_owner(other_user)
        other_league.add_contributor(user)
        LeagueRepository.save_league(other_league)
        other_user.add_league(other_league.id)
        user.add_league(other_league.id)

        # finally, save users to record all league associations
        UserRepository.save_user(user)
        UserRepository.save_user(other_user)
        
        return flask.redirect("/profile")

    @classmethod
    def clear_db(cls):
        if not cls.DEV_ENVIRONMENT:
            user = super().get_auth_user()
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error",
                "message": "This feature is only available in the development environment."
            })
        
        DevLocalDB.clear_db()
        flask.session.clear()

        return flask.redirect("/")