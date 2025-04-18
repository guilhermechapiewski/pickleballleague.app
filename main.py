import os
import logging
import flask
from app.controllers import RootController, UserController, LeagueController, SeriesController, DevController

DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"

try:
    import version #auto-generated by "make deploy"
except ImportError:
    version = type('Version', (), {'git_commit': 'HEAD', 'deploy_timestamp': 'N/A'})()

try:
    from secret import FLASK_SECRET_KEY
    if DEV_ENVIRONMENT:
        FLASK_SECRET_KEY = os.urandom(24)
except ImportError:
    FLASK_SECRET_KEY = os.urandom(24)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = flask.Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

@app.route("/")
def index():
    return RootController.index(version)

@app.route("/sign-in", methods=["POST"])
def sign_in():
    return UserController.sign_in()

@app.route("/sign-out")
def sign_out():
    return UserController.sign_out()

@app.route("/create-league", methods=["POST"])
def create_league():
    return LeagueController.create_league()

@app.route("/save_league", methods=["POST"])
def save_league():
    return LeagueController.save_league()

@app.route("/league/<league_id>")
def get_league(league_id):
    return LeagueController.get_league(league_id)

@app.route("/league/<league_id>/delete")
def delete_league(league_id):
    return LeagueController.delete_league(league_id)

@app.route("/create-series", methods=["POST"])
def create_series():
    return SeriesController.create_series()

@app.route("/series/<series_id>")
def get_series(series_id):
    return SeriesController.get_series(series_id)

@app.route("/series/<series_id>/delete")
def delete_series(series_id):
    return SeriesController.delete_series(series_id)

@app.route("/series/<series_id>/league/<league_id>/remove")
def remove_league_from_series(series_id, league_id):
    return SeriesController.remove_league_from_series(series_id, league_id)

@app.route("/series/<series_id>/league/add", methods=["POST"])
def add_league_to_series(series_id):
    return SeriesController.add_league_to_series(series_id)

@app.route("/save_series", methods=["POST"])
def save_series():
    return SeriesController.save_series()

@app.route("/profile")
def get_profile():
    return UserController.get_profile()

@app.route("/dev-load-test-data")
def load_test_data():
    return DevController.load_test_data()

@app.route("/dev-clear-db")
def clear_db():
    return DevController.clear_db()

if __name__ == "__main__":
    logger.info("Running AppEngine server locally")
    app.run(host="127.0.0.1", port=8080, debug=True)