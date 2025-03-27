import os
import logging
import flask
from app.template import TemplateEngine
from app.pickleball import League, ScoringSystem, Player, Series
from app.db import DevLocalDB, LeagueRepository, UserRepository, ShortLinkRepository, SeriesRepository
from app.user import User
from app.links import ShortLink

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

def get_auth_user() -> User:
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
    new_league = flask.request.args.get("new_league")
    return template_engine.render("index", {"version": version, "dev_environment": DEV_ENVIRONMENT, "user": user, "new_league": new_league})

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
    
    return flask.redirect(flask.request.referrer or "/")

@app.route("/sign-out")
def sign_out():
    flask.session.clear()
    return flask.redirect("/")

@app.route("/create-league", methods=["POST"])
def create_league():
    user = get_auth_user()
    
    player_names = flask.request.form.get("player_names")
    league_name = flask.request.form.get("league_name")
    logger.info(f"Creating league name=[{league_name}] for players=[{player_names}]")

    league = League(name=league_name, player_names=player_names)
    league.set_scoring_system(ScoringSystem(flask.request.form.get("scoring_system")))
    
    # TODO: remove this once we have more templates
    #league.set_template(flask.request.form.get("template"))
    league.set_template("ricky")
    
    rounds = int(flask.request.form.get("rounds"))
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
    user = get_auth_user()
    league_id = flask.request.form.get("league_id")
    
    # first check if the short link exists
    short_link = ShortLinkRepository.get_short_link(league_id)
    if short_link:
        league_id = short_link.destination_link
    
    league = LeagueRepository.get_league(league_id)

    if league.get_version() != float(flask.request.form.get("version_control")):
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: Concurrent editing",
            "message": f"This league was updated by another user. Please refresh the page and try again.<br><br>Code: {str(league.get_version())}/{flask.request.form.get('version_control')}",
            "action_name": "Back to league",
            "action_url": f"/league/{league_id}"
        })

    # check if the short link needs to be updated
    update_league_id = flask.request.form.get("update_league_id")
    new_league_id = flask.request.form.get("new_league_id")
    if update_league_id and new_league_id and update_league_id == "1":
        # check if the new short link already exists
        short_link = ShortLinkRepository.get_short_link(new_league_id)
        if short_link:
            logger.error(f"Short link already exists: {new_league_id}")
            return template_engine.render("error", {
                "dev_environment": DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Short link already exists",
                "message": "The short link you are looking for already exists. Please check the URL and try again.",
                "action_name": "Back to league",
                "action_url": f"/league/{league_id}"
            })
        else:
            short_link = ShortLink(new_league_id, league.id)
            ShortLinkRepository.save_short_link(short_link)
            league.set_short_link(new_league_id)
    
    # now update the league name
    update_league_name = flask.request.form.get("update_league_name")
    new_league_name = flask.request.form.get("new_league_name")
    if new_league_name and update_league_name and update_league_name == "1" and new_league_name != "":
        league.name = new_league_name
    
    # now update the league contributors
    update_contributors = flask.request.form.get("update_contributors")
    new_contributor_email = flask.request.form.get("new_contributor_email")
    if update_contributors and update_contributors == "1" and new_contributor_email and new_contributor_email != "":
        contributor = UserRepository.get_user(new_contributor_email)
        if contributor:
            league.add_contributor(contributor)
            contributor.add_league(league.id)
            UserRepository.save_user(contributor)
        else:
            return template_engine.render("error", {
                "dev_environment": DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: User not found",
                "message": f"The contributor you are trying to add (<i>{new_contributor_email}</i>) was not found in the user database.",
                "action_name": "Back to league",
                "action_url": f"/league/{league.id}"
            })
    
    # now update the league player names
    update_player_names = flask.request.form.get("update_player_names")
    if update_player_names and update_player_names == "1":
        all_players = []
        for round in league.schedule:
            match_index = 1
            for match in round.matches:
                player1_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player1")
                player2_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player2")
                player3_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player3")
                player4_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player4")
                
                # Ensure player names are not empty to avoid potential errors
                if player1_name.strip():
                    player1 = Player(player1_name.strip())
                    if player1 not in all_players:
                        all_players.append(player1)
                
                if player2_name.strip():
                    player2 = Player(player2_name.strip())
                    if player2 not in all_players:
                        all_players.append(player2)
                
                if player3_name.strip():
                    player3 = Player(player3_name.strip())
                    if player3 not in all_players:
                        all_players.append(player3)
                
                if player4_name.strip():
                    player4 = Player(player4_name.strip())
                    if player4 not in all_players:
                        all_players.append(player4)
                
                match_index += 1
            
            # Handle players out for this round
            players_out_key = f"players-out-round{round.number}"
            if players_out_key in flask.request.form and flask.request.form.get(players_out_key).strip():
                for player_name in flask.request.form.get(players_out_key).split(","):
                    if player_name.strip():  # Skip empty names
                        player_out = Player(player_name.strip())
                        if player_out not in all_players:
                            all_players.append(player_out)
        
        # Set the updated player list
        league.set_players(all_players)
        
        # Update match players and players out for each round
        for round in league.schedule:
            # Create a copy of all players to track who's out
            remaining_players = all_players.copy()
            match_index = 1
            
            for match in round.matches:
                player1_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player1")
                player2_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player2")
                player3_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player3")
                player4_name = flask.request.form.get(f"player-name-round{round.number}-match{match_index}-player4")
                
                # Create player objects and update match
                if player1_name.strip():
                    player1 = Player(player1_name.strip())
                    match.players[0] = player1
                    # Remove from remaining players if present
                    for player in remaining_players:
                        if player == player1:
                            remaining_players.remove(player)
                            break
                
                if player2_name.strip():
                    player2 = Player(player2_name.strip())
                    match.players[1] = player2
                    # Remove from remaining players if present
                    for player in remaining_players:
                        if player == player2:
                            remaining_players.remove(player)
                            break
                
                if player3_name.strip():
                    player3 = Player(player3_name.strip())
                    match.players[2] = player3
                    # Remove from remaining players if present
                    for player in remaining_players:
                        if player == player3:
                            remaining_players.remove(player)
                            break
                
                if player4_name.strip():
                    player4 = Player(player4_name.strip())
                    match.players[3] = player4
                    # Remove from remaining players if present
                    for player in remaining_players:
                        if player == player4:
                            remaining_players.remove(player)
                            break
                
                match_index += 1
            
            # Set players out for this round
            round.players_out = remaining_players

    # now update the league scores
    for round in league.schedule:
        player_index = 1
        for player in league.players:
            player_score = None
            try:
                player_score = flask.request.form.get(f"player_score_round{round.number}_player{player_index}")
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
    return flask.redirect(f"/league/{league.id}" if not league.short_link else f"/league/{league.short_link}")

@app.route("/league/<league_id>")
def league(league_id):
    user = get_auth_user()
    try:
        # first check if a short link exists to get the actual league_id
        short_link = ShortLinkRepository.get_short_link(league_id)
        if short_link:
            league_id = short_link.destination_link
        
        # retrieve league
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
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
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
                "dev_environment": DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Permission denied",
                "message": "You are not the owner of this league."
            })
    else:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: League not found",
            "message": "The league you are trying to delete does not exist."
        })

@app.route("/create-series", methods=["POST"])
def create_series():
    user = get_auth_user()
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

@app.route("/series/<series_id>")
def series(series_id):
    user = get_auth_user()
    try:
        # retrieve series
        series = SeriesRepository.get_series(series_id)
        return template_engine.render(f"series", {
            "series": series,
            "user": user,
            "dev_environment": DEV_ENVIRONMENT,
            "domain_name": flask.request.host
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception(e)
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: Series not found",
            "message": "The series you are looking for does not exist. Please check the URL and try again."
        })

@app.route("/series/<series_id>/delete")
def delete_series(series_id):
    user = get_auth_user()
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
            return template_engine.render("error", {
                "dev_environment": DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Permission denied",
                "message": "You are not the owner of this series."
            })
    else:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: Series not found",
            "message": "The series you are trying to delete does not exist."
        })

@app.route("/series/<series_id>/league/<league_id>/remove")
def remove_league_from_series(series_id, league_id):
    user = get_auth_user()
    user = UserRepository.get_user(user.email)
    series = SeriesRepository.get_series(series_id)
    league = LeagueRepository.get_league(league_id)
    
    series.remove_league(league_id)
    SeriesRepository.save_series(series)

    user.remove_league(league_id)
    UserRepository.save_user(user)

    return flask.redirect(f"/series/{series_id}")

@app.route("/series/<series_id>/league/add", methods=["POST"])
def add_league_to_series(series_id):
    user = get_auth_user()
    series = SeriesRepository.get_series(series_id)
    league_id = flask.request.form.get("league_id")
    league = LeagueRepository.get_league(league_id)
    
    if not league:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: League not found",
            "message": "The league you are trying to add does not exist."
        })
    
    if series.owner and series.owner.email == user.email:
        series.add_league(league)
        SeriesRepository.save_series(series)
        return flask.redirect(f"/series/{series_id}")
    else:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error: Permission denied",
            "message": "You are not the owner of this series."
        })

@app.route("/save_series", methods=["POST"])
def save_series():
    user = get_auth_user()
    series_id = flask.request.form.get("series_id")
    
    series = SeriesRepository.get_series(series_id)

    # update the series name
    update_series_name = flask.request.form.get("update_series_name")
    new_series_name = flask.request.form.get("new_series_name")
    if new_series_name and update_series_name and update_series_name == "1" and new_series_name != "":
        series.name = new_series_name
    
    SeriesRepository.save_series(series)
    return flask.redirect(f"/series/{series.id}")

@app.route("/profile")
def profile():
    user = get_auth_user()

    if not user:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
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
    return template_engine.render("profile", {
        "dev_environment": DEV_ENVIRONMENT, 
        "user": user, 
        "leagues": leagues,
        "series": series,
        "domain_name": flask.request.host
    })

@app.route("/dev-load-test-data")
def load_test_data():
    if not DEV_ENVIRONMENT:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error",
            "message": "This feature is only available in the development environment."
        })
    
    user = get_auth_user()
    if not user:
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
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

@app.route("/dev-clear-db")
def clear_db():
    if not DEV_ENVIRONMENT:
        user = get_auth_user()
        return template_engine.render("error", {
            "dev_environment": DEV_ENVIRONMENT,
            "user": user,
            "title": "Error",
            "message": "This feature is only available in the development environment."
        })
    
    DevLocalDB.clear_db()
    flask.session.clear()

    return flask.redirect("/")

if __name__ == "__main__":
    logger.info("Running AppEngine server locally")
    app.run(host="127.0.0.1", port=8080, debug=True)