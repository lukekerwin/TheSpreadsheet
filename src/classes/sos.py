import pandas as pd
import warnings
import requests
from src.classes.admin import base_url, session
warnings.filterwarnings('ignore')

def getsos(league_id, season_id, game_type='Regular Season'):
    player_stats = requests.get(f'{base_url}stats/player?league_id={league_id}&season_id={season_id}').json()
    team_stats = requests.get(f'{base_url}stats/team?league_id={league_id}&season_id={season_id}').json()
    goalie_stats = requests.get(f'{base_url}stats/goalie?league_id={league_id}&season_id={season_id}').json()

    pbp = pd.DataFrame(player_stats)
    gpbp = pd.DataFrame(goalie_stats)

    pbp = pbp[pbp['game_type'] == game_type]
    gpbp = gpbp[gpbp['game_type'] == game_type]
    grouped_player_stats = pbp.groupby(['player_id','week'], as_index=False).sum()[['player_id','week','gp','win','loss','otl']]
    grouped_goalie_stats = gpbp.groupby(['player_id','week'], as_index=False).sum()[['player_id','week','gp','win','loss','otl']]
    grouped_player_stats['Wins'] = grouped_player_stats['win']
    grouped_player_stats['Losses'] = grouped_player_stats['loss'] + grouped_player_stats['otl']
    grouped_goalie_stats['Wins'] = grouped_goalie_stats['win']
    grouped_goalie_stats['Losses'] = grouped_goalie_stats['loss'] + grouped_goalie_stats['otl']
    grouped_player_stats_ = grouped_player_stats[['player_id','Wins','Losses']]
    grouped_goalie_stats_ = grouped_goalie_stats[['player_id','Wins','Losses']]
    grouped_stats = pd.concat([grouped_player_stats_, grouped_goalie_stats_])
    grouped_stats = grouped_stats.groupby(['player_id'], as_index=False).sum()

    sos = []
    gsos = []
    for count, game_id in enumerate(pbp['game_id'].unique()):
        player_stats = pbp
        goalie_stats = gpbp

        game_skater_stats = player_stats[player_stats['game_id'] == game_id][['player_id','week','team_id','ecu','gp','win','loss','otl']]
        game_goalie_stats = goalie_stats[goalie_stats['game_id'] == game_id][['player_id','week','team_id','ecu','gp','win','loss','otl']]
        overall_stats = pd.concat([game_skater_stats, game_goalie_stats])
        overall_stats_with_records = overall_stats.merge(grouped_stats, on='player_id', how='left')

        team_agg_records = overall_stats_with_records.groupby(['team_id'], as_index=False).sum()[['team_id','win','loss','otl','Wins','Losses']]
        team_agg_records_adj = team_agg_records.copy()
        team_agg_records_adj['Wins'] = team_agg_records_adj['Wins'] - (team_agg_records_adj['win']+(team_agg_records_adj['otl']/2))
        team_agg_records_adj['Losses'] = team_agg_records_adj['Losses'] - (team_agg_records_adj['loss']+(team_agg_records_adj['otl']/2))
        team_agg_records_adj = team_agg_records_adj[['team_id','Wins','Losses']]
        team_agg_records_adj.columns = ['team_id','TeamW','TeamL']
        copy = team_agg_records_adj.copy()
        copy.columns = ['team_id','OppW','OppL']
        team_agg_records_adj = team_agg_records_adj.join(copy[['OppW','OppL']].reindex(copy.index[::-1]).reset_index(drop=True))
        team_agg_records_adj.columns = ['team_id','TeamW','TeamL','OppW','OppL']

        game_skater_stats_ = game_skater_stats.merge(team_agg_records_adj, on='team_id', how='left')[['player_id','week','TeamW','TeamL','OppW','OppL']]
        game_goalie_stats_ = game_goalie_stats.merge(team_agg_records_adj, on='team_id', how='left')[['player_id','week','TeamW','TeamL','OppW','OppL']]

        sos.append(game_skater_stats_)
        gsos.append(game_goalie_stats_)

        progress = (count+1)/len(pbp['game_id'].unique())*100
        print('Progress: '+str(round(progress,2))+'%', end='\r')

    sos_ = pd.concat(sos)
    gsos_ = pd.concat(gsos)

    sos_grouped = sos_.groupby(['player_id','week'], as_index=False).sum()[['player_id','week','TeamW','TeamL','OppW','OppL']]
    gsos_grouped = gsos_.groupby(['player_id','week'], as_index=False).sum()[['player_id','week','TeamW','TeamL','OppW','OppL']]
    sos_grouped['TeamWp'] = sos_grouped['TeamW']/(sos_grouped['TeamW']+sos_grouped['TeamL'])
    sos_grouped['OppWp'] = sos_grouped['OppW']/(sos_grouped['OppW']+sos_grouped['OppL'])
    gsos_grouped['TeamWp'] = gsos_grouped['TeamW']/(gsos_grouped['TeamW']+gsos_grouped['TeamL'])
    gsos_grouped['OppWp'] = gsos_grouped['OppW']/(gsos_grouped['OppW']+gsos_grouped['OppL'])

    new_sos = grouped_player_stats.merge(sos_grouped, on=['player_id','week'], how='left')[['player_id','week','gp','win','loss','otl','TeamW','TeamL','OppW','OppL','OppWp','TeamWp']]
    new_gsos = grouped_goalie_stats.merge(gsos_grouped, on=['player_id','week'], how='left')[['player_id','week','gp','win','loss','otl','TeamW','TeamL','OppW','OppL','OppWp','TeamWp']]

    weekly_max_gp = new_sos.groupby(['week'], as_index=False).max()[['week','gp']]
    weekly_max_gp.columns = ['week','max_gp']
    records = []
    for row in range(0, len(weekly_max_gp)):
        row = weekly_max_gp.iloc[row]
        for i in range(0, row['max_gp']+1):
            for j in range(0, row['max_gp']+1):
                for k in range(0, row['max_gp']+1):
                    if i+j+k <= row['max_gp'] and i+j+k > 0:
                        records.append({'week':row['week'],'win':i,'loss':j,'otl':k,'points':(i*2)+k, 'possible_points':(i+j+k)*2})

    df = pd.DataFrame(records).sort_values(by=['points'], ascending=False)
    df['p%'] = df['points']/df['possible_points']
    df['net_points'] = df['points']-df['possible_points']

    df = df.sort_values(by=['points','p%','net_points'], ascending=False).reset_index(drop=True)
    df['W%'] = 1-(df.index/len(df))
    df = df[['week','win','loss','otl','W%']]

    weekly_max_gp2 = new_gsos.groupby(['week'], as_index=False).max()[['week','gp']]
    weekly_max_gp2.columns = ['week','max_gp']
    records2 = []
    for row2 in range(0, len(weekly_max_gp2)):
        row2 = weekly_max_gp2.iloc[row2]
        for i in range(0, row2['max_gp']+1):
            for j in range(0, row2['max_gp']+1):
                for k in range(0, row2['max_gp']+1):
                    if i+j+k <= row2['max_gp'] and i+j+k > 0:
                        records2.append({'week':row2['week'],'win':i,'loss':j,'otl':k,'points':(i*2)+k, 'possible_points':(i+j+k)*2})

    df2 = pd.DataFrame(records2).sort_values(by=['points'], ascending=False)
    df2['p%'] = df2['points']/df2['possible_points']
    df2['net_points'] = df2['points']-df2['possible_points']

    df2 = df2.sort_values(by=['points','p%','net_points'], ascending=False).reset_index(drop=True)
    df2['W%'] = 1-(df2.index/len(df2))
    df2 = df2[['week','win','loss','otl','W%']]

    new_sos = new_sos.merge(df, on=['week','win','loss','otl'], how='left')
    new_gsos = new_gsos.merge(df2, on=['week','win','loss','otl'], how='left')

    new_sos['player_rating'] = ((2*new_sos['W%'])+(new_sos['OppWp']))/3
    new_gsos['player_rating'] = ((2*new_gsos['W%'])+(new_gsos['OppWp']))/3
    weekly_new_sos = new_sos[['player_id','week','gp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating']]
    weekly_new_gsos = new_gsos[['player_id','week','gp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating']]
    new_sos = weekly_new_sos.groupby(['player_id'], as_index=False).agg({'gp':'sum','TeamW':'sum','TeamL':'sum','OppW':'sum','OppL':'sum','OppWp':'mean','TeamWp':'mean','player_rating':'mean'})
    new_sos.columns = ['player_id','sgp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating']
    new_gsos = weekly_new_gsos.groupby(['player_id'], as_index=False).agg({'gp':'sum','TeamW':'sum','TeamL':'sum','OppW':'sum','OppL':'sum','OppWp':'mean','TeamWp':'mean','player_rating':'mean'})
    new_gsos.columns = ['player_id','sgp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating']

    true_sos = []
    true_gsos = []
    true_tsos = []

    for count, game_id in enumerate(pbp['game_id'].unique()):
        skater_game_stats = player_stats[(player_stats['game_id'] == game_id)].merge(new_sos, on='player_id', how='left')[['player_id','team_id','week','gp','win','loss','otl','TeamWp','player_rating']]
        goalie_game_stats = goalie_stats[(goalie_stats['game_id'] == game_id)].merge(new_gsos, on='player_id', how='left')[['player_id','team_id','week','gp','win','loss','otl','TeamWp','player_rating']]
        
        grouped_game_stats = pd.concat([skater_game_stats, goalie_game_stats])

        team_agg_ratings = grouped_game_stats.groupby(['team_id'], as_index=False).mean()[['team_id','week','TeamWp']]
        team_agg_ratings.columns = ['team_id','week','TeamRating']
        copy = team_agg_ratings.copy()[['team_id','TeamRating']]
        copy.columns = ['team_id','OppRating']
        team_agg_ratings = team_agg_ratings.join(copy[['OppRating']].reindex(copy.index[::-1]).reset_index(drop=True))
        team_agg_ratings.columns = ['team_id','week','TeamRTG','OppRTG']

        game_skater_stats_ = skater_game_stats.merge(team_agg_ratings[['team_id','TeamRTG','OppRTG']], on='team_id', how='left')[['player_id','week','TeamRTG','OppRTG']]
        game_goalie_stats_ = goalie_game_stats.merge(team_agg_ratings[['team_id','TeamRTG','OppRTG']], on='team_id', how='left')[['player_id','week','TeamRTG','OppRTG']]

        true_sos.append(game_skater_stats_)
        true_gsos.append(game_goalie_stats_)
        true_tsos.append(team_agg_ratings)

        progress = (count+1)/len(pbp['game_id'].unique())*100
        print('SOS Iteration 2: '+str(round(progress,2))+'%', end='\r')
    true_sos = pd.concat(true_sos)
    true_gsos = pd.concat(true_gsos)
    true_tsos = pd.concat(true_tsos)

    true_sos_merged = true_sos.groupby(['player_id','week'], as_index=False).mean()[['player_id','week','TeamRTG','OppRTG']]
    true_sos_merged.columns = ['player_id','week','TeamRTG','OppRTG']
    true_gsos_merged = true_gsos.groupby(['player_id','week'], as_index=False).mean()[['player_id','week','TeamRTG','OppRTG']]
    true_gsos_merged.columns = ['player_id','week','TeamRTG','OppRTG']
    true_tsos_merged = true_tsos.groupby(['team_id','week'], as_index=False).mean()[['team_id','week','TeamRTG','OppRTG']]
    true_tsos_merged.columns = ['team_id','week','TeamRTG','OppRTG']

    sos = weekly_new_sos.merge(true_sos_merged, on=['player_id','week'], how='left')[['player_id','week','gp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating','TeamRTG','OppRTG']]
    gsos = weekly_new_gsos.merge(true_gsos_merged, on=['player_id','week'], how='left')[['player_id','week','gp','TeamW','TeamL','OppW','OppL','OppWp','TeamWp','player_rating','TeamRTG','OppRTG']]
    tsos = true_tsos_merged

    # sos
    week_zero = sos.groupby(['player_id'], as_index=False).agg({'week':'min','gp':'sum','TeamW':'sum','TeamL':'sum','OppW':'sum','OppL':'sum','OppWp':'mean','TeamWp':'mean','player_rating':'mean','TeamRTG':'mean','OppRTG':'mean'})
    week_zero['week'] = 0
    week_zerog = gsos.groupby(['player_id'], as_index=False).agg({'week':'min','gp':'sum','TeamW':'sum','TeamL':'sum','OppW':'sum','OppL':'sum','OppWp':'mean','TeamWp':'mean','player_rating':'mean','TeamRTG':'mean','OppRTG':'mean'})
    week_zerog['week'] = 0
    week_zerot = tsos.groupby(['team_id'], as_index=False).agg({'week':'min','TeamRTG':'mean','OppRTG':'mean'})
    week_zerot['week'] = 0

    if game_type == 'Regular Season':
        gt = 1
    elif game_type == 'Playoffs':
        gt = 2
    else:
        gt = 3

    sos = pd.concat([week_zero,sos]).sort_values(['player_id','week']).reset_index(drop=True)
    sos['league_id'] = league_id
    sos['season_id'] = season_id
    sos['game_type'] = game_type
    sos['id'] = (sos['league_id'].astype(int).astype(str)+sos['season_id'].astype(int).astype(str)+sos['player_id'].astype(int).astype(str)+sos['week'].astype(int).astype(str)+str(gt)).astype(int)
    gsos = pd.concat([week_zerog,gsos]).sort_values(['player_id','week']).reset_index(drop=True)
    gsos['league_id'] = league_id
    gsos['season_id'] = season_id
    gsos['game_type'] = game_type
    gsos['id'] = (gsos['league_id'].astype(int).astype(str)+gsos['season_id'].astype(int).astype(str)+gsos['player_id'].astype(int).astype(str)+gsos['week'].astype(int).astype(str)+str(gt)).astype(int)
    tsos = pd.concat([week_zerot,tsos]).sort_values(['team_id','week']).reset_index(drop=True)
    tsos['league_id'] = league_id
    tsos['season_id'] = season_id
    tsos['game_type'] = game_type
    tsos['id'] = (tsos['league_id'].astype(int).astype(str)+tsos['season_id'].astype(int).astype(str)+tsos['team_id'].astype(int).astype(str)+tsos['week'].astype(int).astype(str)+str(gt)).astype(int)

    requests.post(f'{base_url}sos', json=sos.to_dict('records'))
    requests.post(f'{base_url}gsos', json=gsos.to_dict('records'))
    requests.post(f'{base_url}tsos', json=tsos.to_dict('records'))