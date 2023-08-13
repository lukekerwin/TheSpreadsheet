import requests
import pandas as pd
from src.classes.admin import base_url


def getRosters(league_id, season_id, game_type='Regular Season', week='all'):
    if week == 'all':
        players = pd.DataFrame(requests.get(f'{base_url}stats/player?&game_type={game_type}&league_id={league_id}&season_id={season_id}').json())
        goalies = pd.DataFrame(requests.get(f'{base_url}stats/goalie?&game_type={game_type}&league_id={league_id}&season_id={season_id}').json())
    else:
        players = pd.DataFrame(requests.get(f'{base_url}stats/player?&game_type={game_type}&league_id={league_id}&season_id={season_id}&week={week}').json())
        goalies = pd.DataFrame(requests.get(f'{base_url}stats/goalie?&game_type={game_type}&league_id={league_id}&season_id={season_id}&week={week}').json())
    
    weekly = players.groupby(by=['player_id','week','league_id','season_id','game_type'], as_index=False)['team_id'].agg(lambda x: x.mode()[0])
    weeklyg = goalies.groupby(by=['player_id','week','league_id','season_id','game_type'], as_index=False)['team_id'].agg(lambda x: x.mode()[0])
    weekly['last_week'] = weekly.groupby(by=['player_id','league_id','season_id','game_type'])['week'].transform('max')
    weeklyg['last_week'] = weeklyg.groupby(by=['player_id','league_id','season_id','game_type'])['week'].transform('max')
    weekly = pd.concat([weekly, weekly.loc[weekly['week']==weekly['last_week']].assign(week=0)])
    weeklyg = pd.concat([weeklyg, weeklyg.loc[weeklyg['week']==weeklyg['last_week']].assign(week=0)])
    weekly = weekly.drop(columns=['last_week'])
    weeklyg = weeklyg.drop(columns=['last_week'])
    weekly = pd.concat([weekly, weeklyg])
    if game_type == 'Regular Season':
        gt = 1
    elif game_type == 'Playoffs':
        gt = 2
    else:
        gt = 3
    weekly['id'] = weekly['player_id'].astype(str) + weekly['week'].astype(str) + weekly['league_id'].astype(str) + weekly['season_id'].astype(str) + str(gt)
    weekly = weekly.drop_duplicates(subset=['id']).reset_index(drop=True)
    requests.post(f'{base_url}wrosters', json=weekly.to_dict('records')).reason