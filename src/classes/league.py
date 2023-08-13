from src.classes.admin import base_url, session

class League:
    def __init__(self, league_id):
        leagues = session.get(f"{base_url}leagueinfo", params={'all': 'true'}).json()
        try:
            self.league_id = league_id
            self.page_id = [league['page_id'] for league in leagues if league['league_id'] == league_id][0]
            self.league_name = [league['league_name'] for league in leagues if league['league_id'] == league_id][0]
            self.current_season = [league['current_season'] for league in leagues if league['league_id'] == league_id][0]
            self.master_league_id = [league['master_league_id'] for league in leagues if league['league_id'] == league_id][0]
        except:
            raise Exception(f"Invalid League ID: {league_id}")
