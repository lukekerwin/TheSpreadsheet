import requests
import pandas as pd
import numpy as np
import warnings
from src.classes.admin import base_url
warnings.filterwarnings('ignore')

def generate_wars(league_id, season_id, game_type='Regular Season', week='all'):
    accepted_game_types = ['Regular Season', 'Playoffs', 'Pre-Season']
    if game_type not in accepted_game_types:
        raise ValueError('game_type must be one of: {}'.format(accepted_game_types))
    
    if game_type == 'Regular Season':
        gt = 1
    elif game_type == 'Playoffs':
        gt = 2
    else:
        gt = 3
    
    if week == 'all':
        requests.delete(f'{base_url}pwar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&game_type='+str(game_type))
        requests.delete(f'{base_url}gwar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&game_type='+str(game_type))
        requests.delete(f'{base_url}twar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&game_type='+str(game_type))
        player_stats = requests.get(f'{base_url}stats/player?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
        goalie_stats = requests.get(f'{base_url}stats/goalie?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
        team_stats = requests.get(f'{base_url}stats/team?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
        player_sos = requests.get(f'{base_url}sos?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
        goalie_sos = requests.get(f'{base_url}gsos?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
        team_sos = requests.get(f'{base_url}tsos?league_id={league_id}&season_id={season_id}&game_type={game_type}').json()
    else:
        requests.delete(f'{base_url}pwar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&week='+str(week)+'&game_type='+str(game_type))
        requests.delete(f'{base_url}gwar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&week='+str(week)+'&game_type='+str(game_type))
        requests.delete(f'{base_url}twar?league_id='+str(league_id)+'&season_id='+str(season_id)+'&week='+str(week)+'&game_type='+str(game_type))
        player_stats = requests.get(f'{base_url}stats/player?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
        goalie_stats = requests.get(f'{base_url}stats/goalie?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
        team_stats = requests.get(f'{base_url}stats/team?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
        player_sos = requests.get(f'{base_url}sos?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
        goalie_sos = requests.get(f'{base_url}gsos?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
        team_sos = requests.get(f'{base_url}tsos?league_id={league_id}&season_id={season_id}&game_type={game_type}&week={week}').json()
    
    player_stats = pd.DataFrame(player_stats)
    goalie_stats = pd.DataFrame(goalie_stats)
    team_stats = pd.DataFrame(team_stats)
    player_sos = pd.DataFrame(player_sos).drop(columns=['id','gp'])
    goalie_sos = pd.DataFrame(goalie_sos).drop(columns=['id','gp'])
    team_sos = pd.DataFrame(team_sos).drop(columns=['id'])

    player_stats_agg = {
        'ecu':'sum',
        'gwg':'sum',
        'points':'sum',
        'goals':'sum',
        'assists':'sum',
        'plusminus':'sum',
        'toi':'sum',
        'twp':'sum',
        'shots':'sum',
        'shots_att':'sum',
        'dekes':'sum',
        'passing_per':'mean',
        'sauce_passes':'sum',
        'hits':'sum',
        'takeaways':'sum',
        'giveaways':'sum',
        'blocks':'sum',
        'interceptions':'sum',
        'pim':'sum',
        'pen_drawn':'sum',
        'pk_clears':'sum',
        'team_score':'sum',
        'team_goals':'sum',
        'team_shots':'sum',
        'team_hits':'sum',
        'team_toa':'sum',
        'team_passingper':'mean',
        'team_fow':'sum',
        'team_pim':'sum',
        'team_ppg':'sum',
        'team_ppa':'sum',
        'team_ppmin':'sum',
        'team_shg':'sum',
        'opp_score':'sum',
        'opp_goals':'sum',
        'opp_shots':'sum',
        'opp_hits':'sum',
        'opp_toa':'sum',
        'opp_passingper':'mean',
        'opp_fow':'sum',
        'opp_pim':'sum',
        'opp_ppg':'sum',
        'opp_ppa':'sum',
        'opp_ppmin':'sum',
        'opp_shg':'sum',
        'p1g':'sum',
        'p2g':'sum',
        'p3g':'sum',
        'otg':'sum',
        'otgp':'sum',
        'opp_p1g':'sum',
        'opp_p2g':'sum',
        'opp_p3g':'sum',
        'opp_otg':'sum',
        'opp_otgp':'sum',
        'win':'sum',
        'loss':'sum',
        'otl':'sum',
        'otw':'sum',
        'gp':'sum',
        'team_ecu':'sum',
        'team_gwg':'sum',
        'team_points':'sum',
        'team_assists':'sum',
        'team_plusminus':'sum',
        'team_toi':'sum',
        'team_twp':'sum',
        'team_shots_att':'sum',
        'team_dekes':'sum',
        'team_passing_per':'mean',
        'team_sauce_passes':'sum',
        'team_takeaways':'sum',
        'team_giveaways':'sum',
        'team_blocks':'sum',
        'team_interceptions':'sum',
        'team_pen_drawn':'sum',
        'team_pk_clears':'sum',
        'opp_ecu':'sum',
        'opp_gwg':'sum',
        'opp_points':'sum',
        'opp_assists':'sum',
        'opp_plusminus':'sum',
        'opp_toi':'sum',
        'opp_twp':'sum',
        'opp_shots_att':'sum',
        'opp_dekes':'sum',
        'opp_passing_per':'mean',
        'opp_sauce_passes':'sum',
        'opp_takeaways':'sum',
        'opp_giveaways':'sum',
        'opp_blocks':'sum',
        'opp_interceptions':'sum',
        'opp_pen_drawn':'sum',
        'opp_pk_clears':'sum',
        'team_save_pct':'mean',
        'team_ga':'sum',
        'team_saves':'sum',
        'team_gaa':'mean',
        'team_pokechecks':'sum',
        'team_diving_saves':'sum',
        'team_breakaways':'sum',
        'team_penalty_shots':'sum',
        'opp_save_pct':'mean',
        'opp_ga':'sum',
        'opp_saves':'sum',
        'opp_gaa':'mean',
        'opp_pokechecks':'sum',
        'opp_diving_saves':'sum',
        'opp_breakaways':'sum',
        'opp_penalty_shots':'sum'}

    player_stats_grouped = player_stats.groupby(['player_id','league_id','season_id','game_type','week','pg']).agg(player_stats_agg).reset_index()

    player_stats_season = player_stats.groupby(['player_id','league_id','season_id','game_type','pg']).agg(player_stats_agg).reset_index()
    player_stats_season['week'] = 0
    players = pd.concat([player_stats_grouped,player_stats_season]).reset_index(drop=True)

    goalie_stats_agg = {
    'breakaways':'sum',
    'diving_saves':'sum',
    'ecu':'sum',
    'ga':'sum',
    'gaa':'mean',
    'gp':'sum',
    'loss':'sum',
    'opp_assists':'sum',
    'opp_blocks':'sum',
    'opp_breakaways':'sum',
    'opp_dekes':'sum',
    'opp_diving_saves':'sum',
    'opp_ecu':'sum',
    'opp_fow':'sum',
    'opp_ga':'sum',
    'opp_gaa':'sum',
    'opp_giveaways':'sum',
    'opp_goals':'sum',
    'opp_gwg':'sum',
    'opp_hits':'sum',
    'opp_interceptions':'sum',
    'opp_otg':'sum',
    'opp_otgp':'sum',
    'opp_p1g':'sum',
    'opp_p2g':'sum',
    'opp_p3g':'sum',
    'opp_passing_per':'mean',
    'opp_passingper':'mean',
    'opp_pen_drawn':'sum',
    'opp_penalty_shots':'sum',
    'opp_pim':'sum',
    'opp_pk_clears':'sum',
    'opp_plusminus':'sum',
    'opp_points':'sum',
    'opp_pokechecks':'sum',
    'opp_ppa':'sum',
    'opp_ppg':'sum',
    'opp_ppmin':'sum',
    'opp_sauce_passes':'sum',
    'opp_save_pct':'mean',
    'opp_saves':'sum',
    'opp_score':'sum',
    'opp_shg':'sum',
    'opp_shots':'sum',
    'opp_shots_att':'sum',
    'opp_takeaways':'sum',
    'opp_toa':'sum',
    'opp_toi':'sum',
    'opp_twp':'sum',
    'otg':'sum',
    'otgp':'sum',
    'otl':'sum',
    'otw':'sum',
    'p1g':'sum',
    'p2g':'sum',
    'p3g':'sum',
    'penalty_shots':'sum',
    'pokechecks':'sum',
    'save_pct':'mean',
    'saves':'sum',
    'shots':'sum',
    'team_assists':'sum',
    'team_blocks':'sum',
    'team_breakaways':'sum',
    'team_dekes':'sum',
    'team_diving_saves':'sum',
    'team_ecu':'sum',
    'team_fow':'sum',
    'team_ga':'sum',
    'team_gaa':'mean',
    'team_giveaways':'sum',
    'team_goals':'sum',
    'team_gwg':'sum',
    'team_hits':'sum',
    'team_interceptions':'sum',
    'team_passing_per':'mean',
    'team_passingper':'mean',
    'team_pen_drawn':'sum',
    'team_penalty_shots':'sum',
    'team_pim':'sum',
    'team_pk_clears':'sum',
    'team_plusminus':'sum',
    'team_points':'sum',
    'team_pokechecks':'sum',
    'team_ppa':'sum',
    'team_ppg':'sum',
    'team_ppmin':'sum',
    'team_sauce_passes':'sum',
    'team_save_pct':'mean',
    'team_saves':'sum',
    'team_score':'sum',
    'team_shg':'sum',
    'team_shots':'sum',
    'team_shots_att':'sum',
    'team_takeaways':'sum',
    'team_toa':'sum',
    'team_toi':'sum',
    'team_twp':'sum',
    'win':'sum'}

    goalie_stats_grouped = goalie_stats.groupby(['player_id','league_id','season_id','game_type','week','pg']).agg(goalie_stats_agg).reset_index()
    goalie_stats_season = goalie_stats.groupby(['player_id','league_id','season_id','game_type','pg']).agg(goalie_stats_agg).reset_index()
    goalie_stats_season['week'] = 0
    goalies = pd.concat([goalie_stats_grouped,goalie_stats_season]).reset_index(drop=True)

    team_stats_agg = {
    'gp':'sum',
    'loss':'sum',
    'opp_assists':'sum',
    'opp_blocks':'sum',
    'opp_breakaways':'sum',
    'opp_dekes':'sum',
    'opp_diving_saves':'sum',
    'opp_ecu':'sum',
    'opp_fow':'sum',
    'opp_ga':'sum',
    'opp_gaa':'mean',
    'opp_giveaways':'sum',
    'opp_goals':'sum',
    'opp_gwg':'sum',
    'opp_hits':'sum',
    'opp_interceptions':'sum',
    'opp_otg':'sum',
    'opp_otgp':'sum',
    'opp_p1g':'sum',
    'opp_p2g':'sum',
    'opp_p3g':'sum',
    'opp_passing_per':'mean',
    'opp_passingper':'mean',
    'opp_pen_drawn':'sum',
    'opp_penalty_shots':'sum',
    'opp_pim':'sum',
    'opp_pk_clears':'sum',
    'opp_plusminus':'sum',
    'opp_points':'sum',
    'opp_pokechecks':'sum',
    'opp_ppa':'sum',
    'opp_ppg':'sum',
    'opp_ppmin':'sum',
    'opp_sauce_passes':'sum',
    'opp_save_pct':'mean',
    'opp_saves':'sum',
    'opp_score':'sum',
    'opp_shg':'sum',
    'opp_shots':'sum',
    'opp_shots_att':'sum',
    'opp_takeaways':'sum',
    'opp_toa':'sum',
    'opp_toi':'sum',
    'opp_twp':'sum',
    'otg':'sum',
    'otgp':'sum',
    'otl':'sum',
    'otw':'sum',
    'p1g':'sum',
    'p2g':'sum',
    'p3g':'sum',
    'team_assists':'sum',
    'team_blocks':'sum',
    'team_breakaways':'sum',
    'team_dekes':'sum',
    'team_diving_saves':'sum',
    'team_ecu':'sum',
    'team_fow':'sum',
    'team_ga':'sum',
    'team_gaa':'mean',
    'team_giveaways':'sum',
    'team_goals':'sum',
    'team_gwg':'sum',
    'team_hits':'sum',
    'team_interceptions':'sum',
    'team_passing_per':'mean',
    'team_passingper':'mean',
    'team_pen_drawn':'sum',
    'team_penalty_shots':'sum',
    'team_pim':'sum',
    'team_pk_clears':'sum',
    'team_plusminus':'sum',
    'team_points':'sum',
    'team_pokechecks':'sum',
    'team_ppa':'sum',
    'team_ppg':'sum',
    'team_ppmin':'sum',
    'team_sauce_passes':'sum',
    'team_save_pct':'mean',
    'team_saves':'sum',
    'team_score':'sum',
    'team_shg':'sum',
    'team_shots':'sum',
    'team_shots_att':'sum',
    'team_takeaways':'sum',
    'team_toa':'sum',
    'team_toi':'sum',
    'team_twp':'sum',
    'win':'sum'}

    team_stats_grouped = team_stats.groupby(['team_id','league_id','season_id','game_type','week']).agg(team_stats_agg).reset_index()
    team_stats_season = team_stats.groupby(['team_id','league_id','season_id','game_type']).agg(team_stats_agg).reset_index()
    team_stats_season['week'] = 0
    teams = pd.concat([team_stats_grouped,team_stats_season]).reset_index(drop=True)

    players_ = players.merge(player_sos,how='inner',on=['player_id','league_id','season_id','game_type','week'])
    goalies_ = goalies.merge(goalie_sos,how='inner',on=['player_id','league_id','season_id','game_type','week'])
    teams_ = teams.merge(team_sos,how='inner',on=['team_id','league_id','season_id','game_type','week'])
    
    _players = []
    _goalies = []
    _teams = []
    for week in players_.week.unique():
        print(f'Processing week {week}...')
        p = players_[players_.week==week]
        g = goalies_[goalies_.week==week]
        t = teams_[teams_.week==week]

        if week == 0:
            wingers = p[p['pg']=='W'].sort_values('toi',ascending=False).head(len(t)*6)
            centers = p[p['pg']=='C'].sort_values('toi',ascending=False).head(len(t)*3)
            forwards = p[p['pg'].isin(['W','C'])].sort_values('toi',ascending=False).head(len(t)*9)
            forwards['pg'] = 'F'
            defensemen = p[p['pg']=='D'].sort_values('toi',ascending=False).head(len(t)*6)
            goalies = g.sort_values('team_toi',ascending=False).head(len(t)*2)
        else:
            if game_type == 'Regular Season':
                p = p[p['gp']>1]
                g = g[g['gp']>1]
            else:
                p = p[p['gp']>0]
                g = g[g['gp']>0]
            wingers = p[p['pg']=='W'].sort_values('toi',ascending=False).head(len(t)*6)
            centers = p[p['pg']=='C'].sort_values('toi',ascending=False).head(len(t)*3)
            forwards = p[p['pg'].isin(['W','C'])].sort_values('toi',ascending=False).head(len(t)*9)
            forwards['pg'] = 'F'
            defensemen = p[p['pg']=='D'].sort_values('toi',ascending=False).head(len(t)*6)
            goalies = g.sort_values('team_toi',ascending=False).head(len(t)*2)
        
        # Team Analytics
        team_a = t[['team_id', 'league_id', 'season_id', 'game_type', 'week', 'gp']]
        
        team_a['QoC'] = t['OppRTG']
        team_a['QoT'] = t['TeamRTG']
        team_a['corsi_for'] = t['team_shots_att']
        team_a['corsi_against'] = t['opp_shots_att']
        team_a['corsi_pct'] = team_a['corsi_for'] / (team_a['corsi_for'] + team_a['corsi_against'])
        team_a['fenwick_for'] = t['team_shots_att'] - t['opp_blocks']
        team_a['fenwick_against'] = t['opp_shots_att'] - t['team_blocks']
        team_a['fenwick_pct'] = team_a['fenwick_for'] / (team_a['fenwick_for'] + team_a['fenwick_against'])
        team_a['team_shooting_pct'] = t['team_goals'] / t['team_shots']
        team_a['team_save_pct'] = t['team_saves'] / t['opp_shots']
        team_a['pdo'] = team_a['team_shooting_pct'] + team_a['team_save_pct']
        team_a['off_zone_toi'] = t['team_toa'] * 4
        team_a['def_zone_toi'] = t['opp_toa'] * 4
        team_a['neu_zone_toi'] = t['team_toi'] - (team_a['off_zone_toi'] + team_a['def_zone_toi'])
        team_a['off_zone_pct'] = team_a['off_zone_toi'] / t['team_toi']
        team_a['def_zone_pct'] = team_a['def_zone_toi'] / t['team_toi']
        team_a['neu_zone_pct'] = team_a['neu_zone_toi'] / t['team_toi']
        team_a['off_zone_giveaways'] = t['team_giveaways'] * team_a['off_zone_pct']
        team_a['def_zone_giveaways'] = t['team_giveaways'] * team_a['def_zone_pct']
        team_a['neu_zone_giveaways'] = t['team_giveaways'] * team_a['neu_zone_pct']
        team_a['off_zone_eff'] = t['team_goals'] / (team_a['off_zone_toi']/3600)
        team_a['off_zone_psc'] = t['team_goals'] / (team_a['off_zone_giveaways'])
        team_a['def_zone_eff'] = t['opp_goals'] / (team_a['def_zone_toi']/3600)
        team_a['def_zone_psc'] = t['opp_goals'] / (team_a['def_zone_giveaways'])
        team_a['expected_goals'] = t['team_shots'] * (t['team_goals'].sum() / t['team_shots'].sum())
        team_a['expected_goals_against'] = t['opp_shots'] * (t['opp_goals'].sum() / t['opp_shots'].sum())
        team_a['expected_goal_diff'] = team_a['expected_goals'] - team_a['expected_goals_against']
        team_a['expected_goals_above_avg'] = t['team_goals'] - team_a['expected_goals']
        team_a['expected_goals_against_above_avg'] = team_a['expected_goals_against'] - t['opp_goals']
        team_a['expected_goal_diff_above_avg'] = team_a['expected_goal_diff'] - (t['team_goals'] - t['opp_goals'])
        team_a['points'] = (t['win'] * 2) + t['otl']
        team_a['point_pct'] = team_a['points'] / (t['gp']*2)
        team_a['win_pct'] = t['win'] / t['gp']
        team_a['EV_off'] = (t['team_goals'] - t['team_ppg'] - t['team_shg']) - ((((t['team_goals'] - t['team_ppg'] - t['team_shg'])/t['team_goals']) * t['team_shots']) * (t['team_goals'].sum() / t['team_shots'].sum()))
        team_a['pp_off'] = ((t['team_ppg']/t['team_ppa']) - (t['team_ppg'].sum()/t['team_ppa'].sum())) * t['team_ppa']
        team_a['EV_def'] = (t['opp_goals'] - t['opp_ppg'] - t['opp_shg']) - ((((t['opp_goals'] - t['opp_ppg'] - t['opp_shg'])/t['opp_goals']) * t['opp_shots']) * (t['opp_goals'].sum() / t['opp_shots'].sum()))
        team_a['pk_def'] = ((1-(t['opp_ppg']/t['opp_ppa'])) - (1-(t['opp_ppg'].sum()/t['opp_ppa'].sum()))) * t['opp_ppa']
        team_a['goals_above_replacement'] = team_a['EV_off'] + team_a['pp_off'] + team_a['EV_def'] + team_a['pk_def']
        team_a['wins_above_replacement'] = team_a['goals_above_replacement'] / (t['team_goals'].sum()/t['win'].sum())
        team_a['record'] = t['win'].astype(str) + '-' + t['loss'].astype(str) + '-' + t['otl'].astype(str)

        sorts = {
                'QoC':'desc',
                'QoT':'desc',
                'corsi_for':'desc', 
                'corsi_against':'asc',
                'corsi_pct':'desc',
                'fenwick_for':'desc',
                'fenwick_against':'asc',
                'fenwick_pct':'desc',
                'team_shooting_pct':'desc',
                'team_save_pct':'desc',
                'pdo':'desc',
                'off_zone_pct':'desc',
                'def_zone_pct':'asc',
                'off_zone_giveaways':'asc',
                'def_zone_giveaways':'asc',
                'neu_zone_giveaways':'asc',
                'off_zone_eff':'desc',
                'off_zone_psc':'desc',
                'def_zone_eff':'asc',
                'def_zone_psc':'desc',
                'expected_goals':'desc',
                'expected_goals_against':'asc',
                'expected_goal_diff':'desc',
                'expected_goals_above_avg':'desc',
                'expected_goals_against_above_avg':'asc',
                'expected_goal_diff_above_avg':'desc',
                'points':'desc',
                'point_pct':'desc',
                'win_pct':'desc',
                'EV_off':'desc',
                'pp_off':'desc',
                'EV_def':'desc',
                'pk_def':'desc',
                'goals_above_replacement':'desc',
                'wins_above_replacement':'desc'}
        
        for col in sorts.keys():
            if sorts[col] == 'desc':
                team_a[col+'_per'] = team_a[col].rank(ascending=True, pct=True)
                team_a[col+'_rank'] = team_a[col].rank(ascending=False, method='first')
            else:
                team_a[col+'_per'] = team_a[col].rank(ascending=False, pct=True)
                team_a[col+'_rank'] = team_a[col].rank(ascending=True, method='first')

        team_a['id'] = (team_a['team_id'].astype(str) + team_a['league_id'].astype(str) + team_a['season_id'].astype(str) + str(gt) + team_a['week'].astype(str))#.astype(int)

        _teams.append(team_a)

        # Player Stats
        assists_per_goal = (p['assists'].sum() / p['goals'].sum())
        shooting_per = (p['goals'].sum() / p['shots'].sum())
        powerplayper = (p['team_ppg'].sum() / p['team_ppa'].sum())
        for player_pos in [forwards, wingers, centers, defensemen]:

            shooting_per_pos = (player_pos['goals'].sum() / player_pos['shots'].sum())
            assists_per_goal_pos = (player_pos['team_assists'].sum() / player_pos['team_goals'].sum())

            player_a = player_pos[['player_id','league_id','season_id','game_type','week','pg','gp']]
            player_a['QoC'] = player_pos['OppRTG']
            player_a['QoT'] = player_pos['TeamRTG']
            player_a['iOFF_per'] = player_pos['points']/player_pos['team_goals']
            player_a['iDEF_per'] = ((player_pos['takeaways']+player_pos['interceptions']) / (player_pos['team_takeaways']+player_pos['team_interceptions']))
            idef = np.where(player_pos['pg'] == 'D', ((player_pos['takeaways']+player_pos['interceptions']) / ((player_pos['team_interceptions']+player_pos['team_takeaways'])*(player_pos['opp_toa']/(player_pos['team_toa']+player_pos['opp_toa'])))), ((player_pos['takeaways']+player_pos['interceptions']) / (player_pos['team_takeaways']+player_pos['team_interceptions'])))
            player_a['corsi_for'] = player_pos['shots_att']
            player_a['team_corsi_for'] = player_pos['team_shots_att']
            player_a['team_corsi_against'] = player_pos['opp_shots_att']
            player_a['team_corsi_pct'] = player_pos['team_shots_att'] / (player_pos['team_shots_att'] + player_pos['opp_shots_att'])
            player_a['fenwick_for'] = player_pos['shots_att'] - np.floor(((player_pos['blocks'].sum()/player_pos['shots_att'].sum())*(player_pos['shots_att'])))
            player_a['team_fenwick_for'] = player_pos['team_shots_att'] - player_pos['opp_blocks']
            player_a['team_fenwick_against'] = player_pos['opp_shots_att'] - player_pos['team_blocks']
            player_a['team_fenwick_pct'] = player_pos['team_shots_att'] / (player_pos['team_shots_att'] + player_pos['opp_shots_att'] - player_pos['opp_blocks'] - player_pos['team_blocks'])
            player_a['team_shooting_pct'] = player_pos['team_goals'] / player_pos['team_shots']
            player_a['team_save_pct'] = (player_pos['opp_shots'] - player_pos['opp_goals']) / player_pos['opp_shots']
            player_a['pdo'] = player_a['team_shooting_pct'] + player_a['team_save_pct']
            player_a['off_zone_toi'] = player_pos['team_toa']*4
            player_a['def_zone_toi'] = player_pos['opp_toa']*4
            player_a['neu_zone_toi'] = player_pos['toi'] - ((player_pos['team_toa'] - player_pos['opp_toa'])*4)
            player_a['off_zone_pct'] = player_a['off_zone_toi'] / player_pos['toi']
            player_a['def_zone_pct'] = player_a['def_zone_toi'] / player_pos['toi']
            player_a['neu_zone_pct'] = player_a['neu_zone_toi'] / player_pos['toi']
            player_a['off_zone_giveaways'] = player_pos['giveaways'] * player_a['off_zone_pct']
            player_a['def_zone_giveaways'] = player_pos['giveaways'] * player_a['def_zone_pct']
            player_a['neu_zone_giveaways'] = player_pos['giveaways'] * player_a['neu_zone_pct']
            player_a['off_zone_eff'] = player_pos['points'] / player_a['off_zone_toi']
            player_a['off_zone_psc'] = player_pos['giveaways'] / player_a['off_zone_toi']
            player_a['def_zone_eff'] = (player_pos['opp_goals'] / player_a['def_zone_toi'])*idef
            player_a['def_zone_psc'] = player_pos['giveaways'] / player_a['def_zone_toi']
            player_a['expected_goals'] = player_pos['shots'] * (player_pos['goals'].sum()/player_pos['shots_att'].sum())
            player_a['expected_goals_above_avg'] = player_a['expected_goals'] - (player_pos['goals'].sum()/player_pos['shots_att'].sum())
            player_a['Thru_per'] = player_pos['shots'] / player_pos['shots_att']

            player_a['GaX'] = player_pos['goals'] - ((player_pos['goals'].sum() / player_pos['shots'].sum()) * player_pos['shots'])
            player_a['AaX'] = ((player_pos['assists']/(player_pos['team_goals'] - player_pos['goals'])) - (player_pos['assists']/(player_pos['team_goals'] - player_pos['goals'])).mean()) * player_pos['assists']
            player_a['EVO'] = player_a['GaX'] + player_a['AaX']
            player_a['EVD'] = ((player_pos['opp_shots'] * (players_['goals'].sum() / players_['shots'].sum())) - player_pos['opp_goals']) * ((player_pos['interceptions'] + player_pos['takeaways']) / (player_pos['team_interceptions'] + player_pos['team_takeaways']))

            player_a['PPO'] = (((player_pos['team_ppg']/player_pos['team_ppa']) - (player_pos['team_ppg']/player_pos['team_ppa']).mean()) * player_pos['team_ppg']) * (player_pos['points']/player_pos['team_points'])
            player_a['SHD'] = ((-((player_pos['opp_ppg']/player_pos['opp_ppa']) - (player_pos['opp_ppg']/player_pos['opp_ppa']).mean())) * player_pos['opp_ppg']) * ((player_pos['interceptions'] + player_pos['takeaways']) / (player_pos['team_interceptions'] + player_pos['team_takeaways']))
            
            player_a['pTAKE'] = (player_pos['pim']/120) * -((player_pos['opp_ppg']/player_pos['opp_ppa']))
            player_a['pDRAW'] = (player_pos['pen_drawn']) * ((player_pos['team_ppg']/player_pos['team_ppa']))

            player_a['GAR'] = player_a['EVO'] + player_a['EVD']
            player_a['GAR_adj']  = np.where(player_a['GAR'] > 0, player_a['GAR'] * ((player_pos['OppRTG'] - player_pos['OppRTG'].mean()) + 1), -(abs(player_a['GAR']) * (1/((player_pos['OppRTG'] - player_pos['OppRTG'].mean()) + 1))))
            player_a['GAR60'] = player_a['GAR_adj'] / (player_pos['gp'])
            
            sorts = {
                'QoC':'desc','QoT':'desc', 'iOFF_per':'desc', 'iDEF_per':'desc', 'corsi_for':'desc', 'team_corsi_for':'desc',
                'team_corsi_against':'asc', 'team_corsi_pct':'desc', 'fenwick_for':'desc',
                'team_fenwick_for':'desc', 'team_fenwick_against':'asc', 'team_fenwick_pct':'desc',
                'team_shooting_pct':'desc', 'team_save_pct':'desc', 'pdo':'desc', 'off_zone_pct':'desc', 'def_zone_pct':'asc',
                'expected_goals':'desc', 'expected_goals_above_avg':'desc', 'Thru_per':'desc',
                'GaX':'desc', 'AaX':'desc', 'EVO':'desc', 'EVD':'desc', 'PPO':'desc', 'SHD':'desc', 'pTAKE':'desc', 'pDRAW':'desc', 'GAR':'desc',
                'GAR_adj':'desc', 'GAR60':'desc'
            }

            for col in sorts.keys():
                if sorts[col] == 'desc':
                    player_a[col+'_per'] = player_a[col].rank(ascending=True, pct=True)
                    player_a[col+'_rank'] = player_a[col].rank(ascending=False, method='first')
                else:
                    player_a[col+'_per'] = player_a[col].rank(ascending=False, pct=True)
                    player_a[col+'_rank'] = player_a[col].rank(ascending=True, method='first')
            
            player_a['id'] = (player_a['player_id'].astype(str) + player_a['league_id'].astype(str) + player_a['season_id'].astype(str) + str(gt) + player_a['week'].astype(str)+player_a['pg'].astype(str))
            _players.append(player_a)

            goalie_a = goalies[['player_id','league_id','season_id','game_type','week','pg','gp']]
            mult = goalies['team_pim']/goalies['team_pim'].max()
            goalie_a['QoC'] = goalies['OppRTG']
            goalie_a['QoT'] = goalies['TeamRTG']

            # 5v5
            goalie_a['evSv_per'] = 1 - ((goalies['opp_goals'] - goalies['opp_ppg'] - goalies['opp_shg']) / (goalies['opp_shots']))
            goalie_a['evGAA'] = ((goalies['opp_goals'] - goalies['opp_ppg'] - goalies['opp_shg'])) / (goalies['team_toi']/3600)
            goalie_a['evSH60'] = (goalies['shots']) / (goalies['team_toi']/3600)
            goalie_a['evGSAx'] = ((goalies['shots']*shooting_per) - (goalies['opp_goals'])) * (1-(goalies['opp_ppg']/goalies['opp_goals']))
            goalie_a['evGSAA'] = goalie_a['evGAA'] / goalie_a['evGAA'].mean()
            goalie_a['evFSv_per'] = 1-((goalies['opp_goals'] - goalies['opp_ppg'] - goalies['opp_shg']) / (goalies['opp_shots_att']))
            goalie_a['evGAR'] = goalie_a['evGSAx']
            goalie_a['evGAR_adj'] = np.where(goalie_a['evGAR'] > 0, goalie_a['evGAR'] * ((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1), -(abs(goalie_a['evGAR']) * (1/((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1))))
            goalie_a['evGAR60'] = goalie_a['evGAR_adj'] / ((goalies['team_toi']-goalies['team_pim'])/3600)

            # PK
            goalie_a['pkSv_per'] = 1 - ((goalies['opp_ppg']) / (goalies['opp_shots']))
            goalie_a['pkGAA'] = ((goalies['opp_ppg'])) / (goalies['team_toi']/3600)
            goalie_a['pkSH60'] = (goalies['opp_shots']*mult) / (goalies['team_toi']/3600)
            goalie_a['pkGSAx'] = ((goalies['shots']*shooting_per) - (goalies['opp_goals'])) * ((goalies['opp_ppg']/goalies['opp_goals']))
            goalie_a['pkGSAA'] = goalie_a['pkGAA'] / goalie_a['pkGAA'].fillna(0).mean()
            goalie_a['pkFSv_per'] = 1-((goalies['opp_ppg']) / (goalies['opp_shots_att']))
            goalie_a['pkGAR'] = goalie_a['pkGSAx']
            goalie_a['pkGAR_adj'] = np.where(goalie_a['pkGAR'] > 0, goalie_a['pkGAR'] * ((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1), -(abs(goalie_a['pkGAR']) * (1/((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1))))
            goalie_a['pkGAR60'] = goalie_a['pkGAR_adj'] / ((goalies['team_toi'])/3600)

            goalie_a['GAR60'] = (goalies['shots']*shooting_per) - (goalies['opp_goals'])
            goalie_a['GAR60'] = np.where(goalie_a['GAR60'] > 0, goalie_a['GAR60'] * ((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1), -(abs(goalie_a['GAR60']) * (1/((goalies['OppRTG'] - goalies['OppRTG'].mean()) + 1))))
            goalie_a['GAR60'] = goalie_a['GAR60'] / ((goalies['team_toi'])/3600)
            
            goalie_a['OFF'] = goalies['team_goals'] - (goalies['team_shots']*shooting_per)
            goalie_a['DEF'] = goalies['team_toa'] / (goalies['team_toa'] + goalies['opp_toa'])
            goalie_a['PP'] = goalies['team_ppg'] / goalies['team_ppa']
            goalie_a['PK'] = 1-(goalies['opp_ppg'] / goalies['opp_ppa'])

            sorts = {
                'QoC':'desc',
                'QoT':'desc',
                'evSv_per':'desc', 
                'evGAA':'asc', 
                'evSH60':'desc', 
                'evGSAx':'desc', 
                'evGSAA':'asc', 
                'evFSv_per':'desc', 
                'evGAR':'desc', 
                'evGAR_adj':'desc', 
                'evGAR60':'desc',
                'pkSv_per':'desc', 
                'pkGAA':'asc', 
                'pkSH60':'desc', 
                'pkGSAx':'desc', 
                'pkGSAA':'asc', 
                'pkFSv_per':'desc', 
                'pkGAR':'desc', 
                'pkGAR_adj':'desc', 
                'pkGAR60':'desc',
                'GAR60':'desc',
                'OFF':'desc',
                'DEF':'desc',
                'PP':'desc',
                'PK':'desc'
            }
            
            for col in sorts.keys():
                if sorts[col] == 'desc':
                    goalie_a[col+'_per'] = goalie_a[col].rank(ascending=True, pct=True)
                    goalie_a[col+'_rank'] = goalie_a[col].rank(ascending=False, method='first')
                else:
                    goalie_a[col+'_per'] = goalie_a[col].rank(ascending=False, pct=True)
                    goalie_a[col+'_rank'] = goalie_a[col].rank(ascending=True, method='first')
            
            goalie_a['id'] = (goalie_a['player_id'].astype(str)+goalie_a['league_id'].astype(str)+goalie_a['season_id'].astype(str)+str(gt)+goalie_a['week'].astype(str)).astype(int)
            
            _goalies.append(goalie_a.drop_duplicates(subset=['id']))
        
    players = pd.concat(_players)
    goalies = pd.concat(_goalies)
    teams = pd.concat(_teams)

    # replace all inf values with 0
    players = players.replace([np.inf, -np.inf], 0).drop_duplicates(subset=['id']).round(3).fillna(0)
    goalies = goalies.replace([np.inf, -np.inf], 0).drop_duplicates(subset=['id']).round(3).fillna(0)
    teams = teams.replace([np.inf, -np.inf], 0).drop_duplicates(subset=['id']).round(3).fillna(0)

    teams = teams.dropna(subset=['id'])

    r1 = requests.post(f'{base_url}pwar', json=players.to_json(orient='records')).text
    r2 = requests.post(f'{base_url}gwar', json=goalies.to_json(orient='records')).text
    r3 = requests.post(f'{base_url}twar', json=teams.to_json(orient='records')).text
    print(r1, r2, r3)