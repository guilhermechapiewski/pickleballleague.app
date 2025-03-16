import os
import logging
import flask
from app.template import TemplateEngine
from app.pickleball import League, ScoringSystem
from app.db import LeagueRepository, UserRepository
from app.user import User

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

template_engine = TemplateEngine()

def get_auth_user():
    user = None
    # Check if user is already authenticated
    if flask.session.get("user_id") and flask.session.get("user_google_id") and flask.session.get("user_email"):
        user = User()
        user.id = flask.session.get("user_id")
        user.google_id = flask.session.get("user_google_id")
        user.email = flask.session.get("user_email")
    return user

@app.route("/")
def root():
    user = get_auth_user()
    return template_engine.render("index", {"version": version, "dev_environment": DEV_ENVIRONMENT, "user": user})

@app.route("/sign-in", methods=["POST"])
def sign_in():
    user = get_auth_user()

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
    
    return flask.redirect("/")

@app.route("/sign-out")
def sign_out():
    flask.session.clear()
    return flask.redirect("/")

@app.route("/create-league", methods=["POST"])
def create_league():
    user = get_auth_user()
    
    player_names = flask.request.form["player_names"]
    league_name = flask.request.form["league_name"]
    logger.info(f"Creating league name=[{league_name}] for players=[{player_names}]")

    league = League(name=league_name, player_names=player_names)
    league.set_scoring_system(ScoringSystem(flask.request.form["scoring_system"]))
    league.set_template(flask.request.form["template"])
    
    rounds = int(flask.request.form["rounds"])
    if rounds == 0:
        if len(league.players) == 4:
            rounds = 3
        elif len(league.players) == 5:
            rounds = 5
        elif len(league.players) >= 6:
            rounds = 7
    
    if len(league.players) < 4:
        logger.error(f"Invalid number of players: {len(league.players)}")
        return flask.redirect("/")
    
    if (rounds > 4 and len(league.players) <= 4) or (rounds > 6 and len(league.players) <= 5):
        logger.error(f"Invalid number of rounds: {rounds} for {len(league.players)} players")
        return flask.redirect("/")
    
    league.generate_schedule(rounds=rounds)
    league.set_owner(user)
    LeagueRepository.save_league(league)
    
    if user:
        user = UserRepository.get_user(user.email)
        user.add_league(league.id)
        UserRepository.save_user(user)
        logger.info(f"User {user.email} added as owner ofleague {league.id}")
    
    logger.info(f"League created successfully: {league.id}")
    return flask.redirect(f"/league/{league.id}")

@app.route("/save_league", methods=["POST"])
def save_league():
    league_id = flask.request.form["league_id"]
    league = LeagueRepository.get_league(league_id)

    update_league_id = flask.request.form["update_league_id"]
    new_league_id = flask.request.form["new_league_id"]
    if update_league_id and new_league_id and update_league_id == "1":
        other_league = LeagueRepository.get_league(new_league_id)
        if other_league:
            logger.error(f"League already exists: {new_league_id}")
            return template_engine.render("error", {
                "title": "Error: League already exists",
                "message": "The league you are looking for already exists. Please check the URL and try again.",
                "action_name": "Back",
                "action_url": f"/league/{league_id}"
            })
        else:
            league.id = new_league_id
    
    for round in league.schedule:
        player_index = 1
        for player in league.players:
            player_score = None
            try:
                player_score = flask.request.form[f"player_score_round{round.number}_player{player_index}"]
            except KeyError:
                pass

            if player_score:
                for match in round.matches:
                    player_names = [p.name for p in match.players]
                    
                    if player.name in player_names:
                        
                        if match.scoring_system == ScoringSystem.SCORE:
                            match_score = match.score
                            
                            if player.name in player_names[:2]:
                                match_score[0] = int(player_score)
                            else:
                                match_score[1] = int(player_score)
                            
                            match.set_score(match_score)
                        
                        if match.scoring_system == ScoringSystem.W_L:
                            if player.name in player_names[:2]:
                                if player_score == "w":
                                    match.set_winner_team(1)
                                if player_score == "l":
                                    match.set_winner_team(2)
                            else:
                                if player_score == "w":
                                    match.set_winner_team(2)
                                if player_score == "l":
                                    match.set_winner_team(1)
            
            player_index += 1
    
    LeagueRepository.save_league(league)
    return flask.redirect(f"/league/{league.id}")

@app.route("/league/<league_id>")
def league(league_id):
    user = get_auth_user()
    try:
        league = LeagueRepository.get_league(league_id)
        return template_engine.render(f"league_{league.template}", {
            "league": league,
            "width": 80/len(league.players),
            "user": user,
            "dev_environment": DEV_ENVIRONMENT,
            "domain_name": flask.request.host
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return template_engine.render("error", {
            "title": "Error: League not found",
            "message": "The league you are looking for does not exist. Please check the URL and try again."
        })

@app.route("/league/<league_id>/delete")
def delete_league(league_id):
    user = get_auth_user()
    league = LeagueRepository.get_league(league_id)
    if league:
        if league.owner.email == user.email:
            LeagueRepository.delete_league(league_id)
            user = UserRepository.get_user(user.email)
            user.remove_league(league_id)
            UserRepository.save_user(user)
            return flask.redirect("/profile")
        else:
            return template_engine.render("error", {
                "title": "Error: League not found",
                "message": "You are not the owner of this league."
            })
    else:
        return template_engine.render("error", {
            "title": "Error: League not found",
            "message": "The league you are trying to delete does not exist."
        })

@app.route("/profile")
def profile():
    user = get_auth_user()

    if not user:
        return template_engine.render("error", {
            "title": "Error: Not logged in",
            "message": "Please sign in to view your profile."
        })
    # get full user object from database
    user = UserRepository.get_user(user.email)

    leagues = []
    for league_id in user.league_ids:
        league = LeagueRepository.get_league(league_id)
        leagues.append(league)

    logger.info(f"User: {user.to_object()}")
    return template_engine.render("profile", {
        "dev_environment": DEV_ENVIRONMENT, 
        "user": user, 
        "leagues": leagues
    })

if __name__ == "__main__":
    logger.info("Running AppEngine server locally")
    app.run(host="127.0.0.1", port=8080, debug=True)