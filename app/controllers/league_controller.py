import logging
import flask
from app.controllers import BaseController
from app.models import League, ScoringSystem, Player, ShortLink
from app.repositories import LeagueRepository, UserRepository, ShortLinkRepository
from app.template import TemplateEngine

logger = logging.getLogger(__name__)

class LeagueController(BaseController):
    @classmethod
    def create_league(cls):
        user = super().get_auth_user()
        
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
    
    @classmethod
    def save_league(cls):
        user = super().get_auth_user()
        league_id = flask.request.form.get("league_id")
        
        # first check if the short link exists
        short_link = ShortLinkRepository.get_short_link(league_id)
        if short_link:
            league_id = short_link.destination_link
        
        league = LeagueRepository.get_league(league_id)

        if league.get_version() != 0.0 and league.get_version() != float(flask.request.form.get("version_control")):
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: Concurrent editing",
                "message": f"This league was updated by another user. Please refresh the page and try again.<br><br>Error code: {str(league.get_version())},{flask.request.form.get('version_control')}",
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
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
                    "user": user,
                    "title": "Error: Short link already exists",
                    "message": "The short link you chose already exists. Please check the URL and try again.",
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
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
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
    
    @classmethod
    def get_league(cls, league_id: str):
        user = super().get_auth_user()
        try:
            # first check if a short link exists to get the actual league_id
            short_link = ShortLinkRepository.get_short_link(league_id)
            if short_link:
                league_id = short_link.destination_link
            
            # retrieve league
            league = LeagueRepository.get_league(league_id)
            return TemplateEngine.render(f"league_{league.template}", {
                "league": league,
                "width": 80/len(league.players),
                "user": user,
                "dev_environment": cls.DEV_ENVIRONMENT,
                "domain_name": flask.request.host
            })
        except Exception as e:
            logger.error(f"Error: {e}")
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: League not found",
                "message": "The league you are looking for does not exist. Please check the URL and try again."
            })
    
    @classmethod
    def delete_league(cls, league_id: str):
        user = super().get_auth_user()
        league = LeagueRepository.get_league(league_id)

        if league:
            if league.owner.email == user.email:
                LeagueRepository.delete_league(league_id)
                user = UserRepository.get_user(user.email)
                user.remove_league(league_id)
                UserRepository.save_user(user)
                return flask.redirect("/profile")
            else:
                return TemplateEngine.render("error", {
                    "dev_environment": cls.DEV_ENVIRONMENT,
                    "user": user,
                    "title": "Error: Permission denied",
                    "message": "You are not the owner of this league."
                })
        else:
            return TemplateEngine.render("error", {
                "dev_environment": cls.DEV_ENVIRONMENT,
                "user": user,
                "title": "Error: League not found",
                "message": "The league you are trying to delete does not exist."
            })