from src.classes.admin import base_url, session
from src.classes.league import League
from src.classes.season import Season
from src.classes.game import Game
from src.classes.sos import getsos
from src.classes.war import generate_wars
from src.classes.rosters import getRosters
from concurrent.futures import ThreadPoolExecutor


def run_stats_job(league_id, season_id, season_type='Regular Season', week='all'):
    league = League(league_id)
    season = Season(league_id, season_id)

    existing_games = session.get(f"{base_url}stats/goalie", params={'league_id': league_id, 'season_id': season_id, 'game_type': season_type}).json()
    existing_game_ids = [game['game_id'] for game in existing_games]

    games = season.game_ids

    games = games[games['game_type'] == season_type]
    if week != 'all':
        games = games[games['week'] <= week].sort_values('game_id', ascending=True)
    games = games.sort_values('game_id', ascending=True)
    game_ids = games['game_id'].tolist()

    game_ids = [game_id for game_id in game_ids if game_id not in existing_game_ids]
    
    with ThreadPoolExecutor() as executor:
        executor.map(Game, game_ids)

    print('Calculating SOS...')
    sos = getsos(league_id, season_id, season_type)
    print('Done!')
    print('Calculating Advanced Stats...')
    generate_wars(league_id, season_id, season_type)
    print('Done!')
    print('Gathering Rosters...')
    getRosters(league_id, season_id, season_type)
    print('Done!')
    
    return f"Stats Job Complete: {league.league_name} s{season.season_id} {season_type} {week}"