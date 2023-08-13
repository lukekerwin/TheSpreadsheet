from src.classes.admin import base_url, session
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import numpy as np
import requests

def getGameTables(content, game_id):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        tables = pd.read_html(content)

        player_ids = [int(x['href'].split('userid=')[1].split('&')[0]) for x in soup.select('.mobile_only+ .lgftable2 a') if 'team_user' in x['href']]
        player_names_ids = [{'name':x.text,'player_id':int(x['href'].split('userid=')[1].split('&')[0])} for x in soup.select('.mobile_only+ .lgftable2 a') if 'team_user' in x['href']]
        requests.post(f'{base_url}playerinfo', json=player_names_ids)
        player_team_ids = [int(x['src'].split('/team')[-1].split('.')[0]) for x in soup.select('.mobile_only+ .lgftable2 img') if 'team' in x['src']]
        goalie_ids = [int(x['href'].split('userid=')[1].split('&')[0]) for x in soup.select('br+ .lgftable2 a') if 'team_user' in x['href']]
        goalie_team_ids = [int(x['src'].split('/team')[-1].split('.')[0]) for x in soup.select('br+ .lgftable2 img') if 'team' in x['src']]
        team_ids = [int(x['src'].split('/team')[-1].split('.')[0]) for x in soup.select('.profile_float img') if 'team' in x['src']]
        goalie_names_ids = [{'name':x.text,'player_id':int(x['href'].split('userid=')[1].split('&')[0])} for x in soup.select('br+ .lgftable2 a') if 'team_user' in x['href']]
        requests.post(f'{base_url}playerinfo', json=goalie_names_ids)

        team_stats = [x for x in tables if x.columns[0] == 'Team Stats'][0]
        box_score = [x for x in tables if x.columns[0] == 'Period Stats'][0]
        player_stats = [x for x in tables if x.columns[0] == 'Player Stats'][0]
        goalie_stats = [x for x in tables if x.columns[0] == 'Goalie Stats'][0]

        # FORMAT PLAYER STATS
        playerstats = player_stats.copy()
        playerstats.columns = playerstats.iloc[0]
        playerstats = playerstats.drop([0]).reset_index(drop=True)
        if playerstats.columns[1] == 'Player' and playerstats.columns[2] == 'Player':
            playerstats.columns = ['rating','rating','player','points','goals','assists','plusminus','toi','twp','shots','dekes','passing_per','sauce_passes','hits','takeaways','giveaways','blocks','interceptions','pim','pen_drawn','pk_clears','nan','nan']
        else:
            playerstats.columns = ['rating','player','points','goals','assists','plusminus','toi','twp','shots','dekes','passing_per','sauce_passes','hits','takeaways','giveaways','blocks','interceptions','pim','pen_drawn','pk_clears','nan','nan','nan']
        playerstats = playerstats.drop(['rating','nan'],axis=1)

        playerstats['player_id'] = player_ids
        playerstats['team_id'] = player_team_ids
        playerstats['game_id'] = game_id
        playerstats['ecu'] = np.where(playerstats['player'].str.contains('ECU'),1,0)
        playerstats['gwg'] = np.where(playerstats['player'].str.contains('GWG'),1,0)
        playerstats['position'] = playerstats['player'].str.split('(').str[1].str.split(')').str[0]
        playerstats['pg'] = np.where(playerstats['position'].isin(['LW','RW']),'W',np.where(playerstats['position'].isin(['LD','RD']),'D','C'))
        playerstats['points'] = playerstats['points'].astype(int)
        playerstats['goals'] = playerstats['goals'].astype(int)
        playerstats['assists'] = playerstats['assists'].astype(int)
        playerstats['plusminus'] = playerstats['plusminus'].astype(int)
        playerstats['toi'] = playerstats['toi'].str.split(':').str[0].astype(int)*60 + playerstats['toi'].str.split(':').str[1].astype(int)
        playerstats['twp'] = playerstats['twp'].str.split(':').str[0].astype(int)*60 + playerstats['twp'].str.split(':').str[1].astype(int)
        playerstats['shots'], playerstats['shots_att'] = playerstats['shots'].str.split('/').str[0].astype(int), playerstats['shots'].str.split('/').str[1].astype(int)
        playerstats['dekes'] = playerstats['dekes'].astype(int)
        playerstats['passing_per'] = (playerstats['passing_per'].astype(float)/100).round(3)
        playerstats['sauce_passes'] = playerstats['sauce_passes'].astype(int)
        playerstats['hits'] = playerstats['hits'].astype(int)
        playerstats['takeaways'] = playerstats['takeaways'].astype(int)
        playerstats['giveaways'] = playerstats['giveaways'].astype(int)
        playerstats['blocks'] = playerstats['blocks'].astype(int)
        playerstats['interceptions'] = playerstats['interceptions'].astype(int)
        playerstats['pim'] = playerstats['pim'].str.split(':').str[0].astype(int)*60 + playerstats['pim'].str.split(':').str[1].astype(int)
        playerstats['pen_drawn'] = playerstats['pen_drawn'].astype(int)
        playerstats['pk_clears'] = playerstats['pk_clears'].astype(int)
        playerstats = playerstats[['game_id','team_id','player_id','position','pg','ecu','gwg','points','goals','assists','plusminus','toi','twp','shots','shots_att','dekes','passing_per','sauce_passes','hits','takeaways','giveaways','blocks','interceptions','pim','pen_drawn','pk_clears']]

        # FORMAT TEAM PLAYER STATS
        team_player_stats = playerstats.copy()
        team_player_stats = team_player_stats.groupby(['team_id'],as_index=False).agg({'ecu':'sum',
            'gwg':'sum', 'points':'sum', 'goals':'sum', 'assists':'sum', 'plusminus':'sum', 'toi':'max', 'twp':'sum', 'shots':'sum',
            'shots_att':'sum', 'dekes':'sum', 'passing_per':'mean', 'sauce_passes':'sum', 'hits':'sum',
            'takeaways':'sum', 'giveaways':'sum', 'blocks':'sum', 'interceptions':'sum', 'pim':'sum', 'pen_drawn':'sum',
            'pk_clears':'sum'})
        team_player_stats.columns = ['team_'+x if x not in ['team_id'] else x for x in team_player_stats.columns]
        opp_team_player_stats = team_player_stats.copy()
        opp_team_player_stats.columns = ['opp_'+x[5:] for x in opp_team_player_stats.columns]
        opp_team_player_stats = opp_team_player_stats.reindex([1,0], axis=0).reset_index(drop=True)
        team_player_stats = team_player_stats.join(opp_team_player_stats)

        # FORMAT GOALIE STATS
        goaliestats = goalie_stats.copy()
        goaliestats.columns = goaliestats.iloc[0]
        goaliestats = goaliestats.drop([0]).reset_index(drop=True)
        if goaliestats['S'].astype(float).mean() < 1 and goaliestats['S'].astype(float).mean() > 0:
            goaliestats.columns = ['rating','player','shots','save_pct','ga','saves','gaa','pokechecks','diving_saves',
                                'breakaways','penalty_shots','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN']
        else:
            goaliestats.columns = ['rating','rating','player','shots','save_pct','ga','saves','gaa','pokechecks','diving_saves',
                                'breakaways','penalty_shots','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN']
        goaliestats = goaliestats.drop(['rating','NaN'], axis=1)

        goaliestats['player_id'] = goalie_ids
        goaliestats['team_id'] = goalie_team_ids
        goaliestats['game_id'] = game_id
        goaliestats['position'] = 'G'
        goaliestats['pg'] = 'G'
        goaliestats['ecu'] = np.where(goaliestats['player'].str.contains(' ECU'),1,0)
        goaliestats['shots'] = goaliestats['shots'].astype(int)
        goaliestats['save_pct'] = goaliestats['save_pct'].astype(float)
        goaliestats['ga'] = goaliestats['ga'].astype(int)
        goaliestats['saves'] = goaliestats['saves'].astype(int)
        goaliestats['gaa'] = goaliestats['gaa'].astype(float)
        goaliestats['pokechecks'] = goaliestats['pokechecks'].astype(int)
        goaliestats['diving_saves'] = goaliestats['diving_saves'].astype(int)
        goaliestats['breakaways'] = goaliestats['breakaways'].astype(int)
        goaliestats['penalty_shots'] = goaliestats['penalty_shots'].astype(int)
        goaliestats = goaliestats[['game_id','team_id','player_id','position','pg','ecu','shots','save_pct','ga','saves','gaa','pokechecks','diving_saves','breakaways','penalty_shots']]

        # FORMAT TEAM GOALIE STATS
        team_goaliestats = goaliestats.copy()
        team_goaliestats = team_goaliestats.groupby(['team_id'],as_index=False).agg({'ecu':'sum','shots':'sum','save_pct':'mean','ga':'sum','saves':'sum','gaa':'sum','pokechecks':'sum','diving_saves':'sum','breakaways':'sum','penalty_shots':'sum'})
        team_goaliestats.columns = ['team_'+x if x not in ['team_id'] else x for x in team_goaliestats.columns]
        opp_team_goaliestats = team_goaliestats.copy()
        opp_team_goaliestats.columns = ['opp_'+x[5:] for x in opp_team_goaliestats.columns]
        opp_team_goaliestats = opp_team_goaliestats.reindex([1,0], axis=0).reset_index(drop=True)
        team_goaliestats = team_goaliestats.join(opp_team_goaliestats)

        # FORMAT TEAM STATS
        teamstats = team_stats.copy()
        teamstats.columns = [0,1,2]
        teamstats = teamstats.T
        try:
            teamstats.columns = ['team_score','datetime','team_shot_data','team_goals','team_shots','team_hits','team_toa','team_passingper','team_fow',
                            'team_pim','team_pp','team_ppmin','team_shg','team_twp_data','team_twp_data2','week_and_season','edit']
            teamstats = teamstats.drop([1]).reset_index(drop=True)
            teamstats = teamstats.drop(['team_shot_data','team_twp_data','team_twp_data2','edit','week_and_season','datetime'], axis=1)
        except:
            teamstats.columns = ['team_score','datetime','team_shot_data','team_goals','team_shots','team_hits','team_toa','team_passingper','team_fow',
                            'team_pim','team_pp','team_ppmin','team_shg','team_twp_data','team_twp_data2','week_and_season']
            teamstats = teamstats.drop([1]).reset_index(drop=True)
            teamstats = teamstats.drop(['team_shot_data','team_twp_data','team_twp_data2','week_and_season','datetime'], axis=1)

        teamstats['team_id'] = team_ids
        teamstats['game_id'] = game_id
        teamstats['team_score'] = teamstats['team_score'].astype(int)
        teamstats['team_goals'] = teamstats['team_goals'].astype(int)
        teamstats['team_shots'] = teamstats['team_shots'].astype(int)
        teamstats['team_hits'] = teamstats['team_hits'].astype(int)
        teamstats['team_toa'] = teamstats['team_toa'].str.split(':').apply(lambda x: int(x[0])*60+int(x[1])).astype(int)
        teamstats['team_passingper'] = (teamstats['team_passingper'].astype(float)/100).round(3)
        teamstats['team_fow'] = teamstats['team_fow'].astype(int)
        teamstats['team_pim'] = teamstats['team_pim'].str.split(':').apply(lambda x: int(x[0])*60+int(x[1])).astype(int)
        teamstats['team_ppg'] = teamstats['team_pp'].str.split('/').str[0]
        teamstats['team_ppa'] = teamstats['team_pp'].str.split('/').str[1]
        teamstats['team_ppg'] = teamstats['team_ppg'].astype(int)
        teamstats['team_ppa'] = teamstats['team_ppa'].astype(int)
        teamstats['team_ppmin'] = teamstats['team_ppmin'].str.split(':').apply(lambda x: int(x[0])*60+int(x[1])).astype(int)
        teamstats['team_shg'] = teamstats['team_shg'].astype(int)
        teamstats = teamstats[['game_id','team_id','team_score','team_goals','team_shots','team_hits','team_toa','team_passingper','team_fow','team_pim','team_ppg','team_ppa','team_ppmin','team_shg']]

        opp_teamstats = teamstats.copy().drop(['game_id'], axis=1)
        opp_teamstats.columns = ['opp_'+x[5:] for x in opp_teamstats.columns if x not in ['game_id']]
        opp_teamstats = opp_teamstats.reindex([1,0], axis=0).reset_index(drop=True)
        teamstats = teamstats.join(opp_teamstats)

        # FORMAT BOXSCORE
        boxscore = box_score.copy()
        boxscore.columns = boxscore.iloc[0]
        boxscore = boxscore.drop([0]).reset_index(drop=True)
        # sum all columns after the 4th
        boxscore.iloc[:,4:] = sum(boxscore.iloc[:,4:].astype(int))

        if len(boxscore.columns) > 4:
            otbox = boxscore.iloc[:,4:]
            boxscore = boxscore.iloc[:,:4]
            boxscore.columns = ['team','p1g','p2g','p3g']
            boxscore['otg'] = otbox.sum(axis=1)
            boxscore['otgp'] = 1
        else:
            boxscore.columns = ['team','p1g','p2g','p3g']
            boxscore['otg'] = 0
            boxscore['otgp'] = 0
        boxscore_opp = boxscore.copy()
        boxscore_opp.columns = ['opp_' + x for x in boxscore_opp.columns]
        boxscore_opp = boxscore_opp.drop(['opp_team'], axis=1).reindex([1,0]).reset_index(drop=True)
        boxscore = boxscore.join(boxscore_opp)
        boxscore = boxscore.drop(['team'], axis=1)

        # FORMAT TEAM STATS WITH MERGES
        teamstats = teamstats.join(boxscore)
        teamstats['win'] = np.where(teamstats['team_score'] > teamstats['opp_score'], 1, 0)
        teamstats['otl'] = np.where((teamstats['team_score'] < teamstats['opp_score']) & (teamstats['otgp'] == 1), 1, 0)
        teamstats['loss'] = np.where((teamstats['team_score'] < teamstats['opp_score'])&(teamstats['otgp'] == 0), 1, 0)
        teamstats['otw'] = np.where((teamstats['team_score'] > teamstats['opp_score']) & (teamstats['otgp'] == 1), 1, 0)
        teamstats['gp'] = 1
        for col in teamstats.columns:
            if col in team_player_stats.columns and col not in ['game_id','team_id']:
                try:
                    team_player_stats = team_player_stats.drop([col], axis=1)
                except:
                    pass

        teamstats = teamstats.merge(team_player_stats, on=['team_id'], how='left')

        for col in teamstats.columns:
            if col in team_goaliestats.columns and col not in ['game_id','team_id']:
                try:
                    team_goaliestats = team_goaliestats.drop([col], axis=1)
                except:
                    pass
        teamstats = teamstats.merge(team_goaliestats, on=['team_id'], how='left')

        playerstats['id'] = (playerstats['game_id'].astype(str) + playerstats['team_id'].astype(str) + playerstats['player_id'].astype(str))#.astype(int)
        goaliestats['id'] = (goaliestats['game_id'].astype(str) + goaliestats['team_id'].astype(str) + goaliestats['player_id'].astype(str))#.astype(int)
        teamstats['id'] = (teamstats['game_id'].astype(str) + teamstats['team_id'].astype(str))#.astype(int)

        teamstats = teamstats.loc[:, ~teamstats.columns.duplicated()]
        return teamstats, playerstats, goaliestats
    except UnicodeDecodeError:
        print('Error in game: ' + str(game_id))
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


class Game:
    def __init__(self, game_id) -> None:
        self.game_id = game_id
        self.content = self.__getContent()
        self.time = self.__getTime()
        if self.time:
            self.teamstats, self.playerstats, self.goaliestats = self.__preprocess(self.content, self.game_id)
            self.__post()
        else:
            pass

    def __getContent(self):
        r = session.get(f'https://www.leaguegaming.com/forums/index.php?leaguegaming/league&action=league&page=game&gameid={self.game_id}')
        return r.text.replace('%','')
    
    def __getTime(self):
        try:
            soup = BeautifulSoup(self.content, 'html.parser')
            time = soup.select('.mast .alt2+ tr td')[0].text
            week = soup.select('tr:nth-child(15) td')[0].text
            print(week.strip(), end='\r')
            time = re.sub(r'(\d)(st|nd|rd|th)', r'\1', time)
            if 'Game' in time:
                time = time.split('Game')[0]
            datetime_format = "%A %B %d %Y, %I:%M %p"
            time = datetime.strptime(time, datetime_format)
            if time > datetime.now():
                return False
            else:
                return True
        except:
            return False

    def __preprocess(self, content, game_id):
        teamstats, playerstats, goaliestats = getGameTables(content, game_id)
        return teamstats, playerstats, goaliestats
    
    def __post(self):
        if not self.playerstats.empty:          
            session.post(f'{base_url}playerstats', json=self.playerstats.to_json(orient='records'))
        if not self.goaliestats.empty:
            session.post(f'{base_url}goaliestats', json=self.goaliestats.to_json(orient='records'))
        if not self.teamstats.empty:
            session.post(f'{base_url}teamstats', json=self.teamstats.to_json(orient='records'))