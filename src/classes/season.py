from src.classes.admin import base_url, session
from bs4 import BeautifulSoup
import pandas as pd, numpy as np, json
from concurrent.futures import ThreadPoolExecutor
from src.classes.helpers import fix_date

class Season:
    def __init__(self, league_id, season_id) -> None:
        self.league_id = league_id
        self.season_id = season_id
    
    @property
    def standings(self):
        r = session.get(f'https://www.leaguegaming.com/forums/index.php?leaguegaming/league&action=league&page=standing&leagueid={self.league_id}&seasonid={self.season_id}')
        soup = BeautifulSoup(r.text, 'html.parser')
        team_ids, team_names = [x['href'].split('teamid=')[1].split('&')[0] for x in soup.select('.team_box_icon a') if 'teamid' in x['href']], [x.text for x in soup.select('.team_box_icon a') if 'teamid' in x['href']]
        tables = pd.read_html(r.text)
        standings = []
        for table in tables:
            if len(table.columns) == 16:
                table.columns = ['team_name','GP','W','L','OTW','OTL','PTS','STK','GF','GA','DIFF','L10','HOME','AWAY','1GG','NAN']
                standings.append(table)
        standings = pd.concat(standings)
        standings.columns = ['team_name','GP','W','L','OTW','OTL','PTS','STK','GF','GA','DIFF','L10','HOME','AWAY','1GG','NAN']
        standings = standings.drop(columns=['NAN'])
        standings['team_id'] = team_ids
        standings['team_name'] = team_names
        data = [{'team_id': team_id, 'team_name': team_name} for team_id, team_name in zip(team_ids, team_names)]
        session.post(f'{base_url}teaminfo', json=data)
        return standings
    
    @property
    def current_rosters(self):
        r = session.get(f'https://www.leaguegaming.com/forums/index.php?leaguegaming/league&action=league&page=roster&leagueid={self.league_id}&seasonid={self.season_id}')
        soup = BeautifulSoup(r.text, 'html.parser')
        players = soup.select('#content .lgleague')
        players = [{'player_id': int(player['href'].split('userid=')[1].split('&')[0]), 'User': player.text} for player in players]
        team_ids = [int(link['src'].split('/team')[-1].split('.')[0]) for link in soup.select('.team_display_block img') if '/team' in link['src']]
        tables = pd.read_html(r.text)
        rosters = []
        for i in range(len(tables)):
            team = tables[i]
            team_name = team.columns[0]
            if len(team_name) == 2:
                team_name = team_name[0]

            team.columns = team.iloc[0]
            team = team.iloc[1:]
            splits = team[team['User'].str.contains('Forwards')].index
            if len(splits) == 2:
                roster = team.iloc[splits[0]:splits[1]-1]
                roster['roster_status'] = 'R'
                tc = team.iloc[splits[1]+1:]
                tc['roster_status'] = 'TC'
                if roster.iloc[-1]['User'].startswith('Spent:'):
                    roster = roster.iloc[:-1]
                    roster['roster_status'] = 'R'
                try:
                    if tc.iloc[-1]['User'].startswith('Spent:'):
                        tc = tc.iloc[:-1]
                        tc['roster_status'] = 'TC'
                except:
                    pass
                dfs = [roster,tc]
            elif len(splits) == 1:
                roster = team.iloc[splits[0]:]
                try:
                    if roster.iloc[-1]['User'].startswith('Spent:'):
                        roster = roster.iloc[:-1]
                        roster['roster_status'] = 'R'
                except:
                    pass
                roster['roster_status'] = 'R'
                dfs = [roster]
            else:
                dfs = [team]
            def pg(x):
                if x['position'] in ['LW','RW']:
                    return 'W'
                elif x['position'] in ['C']:
                    return 'C'
                elif x['position'] in ['LD','RD']:
                    return 'D'
                else:
                    return 'G'
            for df in dfs:
                # if "Protected" in User, create new column for position group
                df['Protected'] = df['User'].str.contains(' Protected ')
                df['Protected'] = df['Protected'].astype(int)
                df = df[df['User'].str.contains(r'\d')]
                df['position'] = df['User'].str.split('(').str[1].str.split(')').str[0]
                df['position_group'] = df.apply(lambda x: pg(x), axis=1)
                df['status'] = df['User'].str.split(' ').str[-1]
                df.loc[df['User'].str.contains(' O '), 'roster_status'] = 'Owner'
                df.loc[df['User'].str.contains(' O '), 'Protected'] = 1
                df.loc[df['User'].str.contains(' GM '), 'roster_status'] = 'GM'
                df.loc[df['User'].str.contains(' GM '), 'Protected'] = 1
                df.loc[df['User'].str.contains(' AGM '), 'roster_status'] = 'AGM'
                df.loc[df['User'].str.contains(' AGM '), 'Protected'] = 1
                df.loc[(df['User'].str.contains(' AGM ')) & (df['$'].str.contains(r'\d')), 'roster_status'] = 'PAGM'
                df['User'] = ((((((df['User'].str.split(' O ').str[0]+' ').str.split('(').str[0]).str.replace(' GM', '')).str.replace(' AGM', '').str.replace(' AHL Protected', '').str.replace(' CHL Protected', '')).str.split('.').str[-1]).str.lstrip('0123456789.- ')).str[:-1]
                
                df['$'] = df['$'].str.split('$').str[1]#.str.replace(',','')
                def formatcont(x):
                    if str(x['$']) != 'nan':
                        return x['$'].replace(',','')
                    else:
                        return 0
                df['$'] = df.apply(lambda x: formatcont(x), axis=1)
                df = df.merge(pd.DataFrame(players), how='left', on='User')
                df = df[['player_id','User','position','position_group','roster_status','status','$', 'Protected']]
                df.columns = ['player_id','player_name','position','position_group','roster_status','status','contract','protected']
                df['league_id'] = self.league.league_id
                df['season_id'] = self.season_id
                df['team_name'] = team_name
                df['team_id'] = team_ids[i]
                df = df.dropna(subset=['player_id'])
                df['player_id'] = df['player_id'].astype(int)
                df['id'] = (df['player_id'].astype(str) + df['league_id'].astype(str) + df['season_id'].astype(str)).astype(int)
                rosters.append(df)
        rosters = pd.concat(rosters)
        session.post(f'{base_url}rosters', json=rosters.to_dict(orient='records'))
        return rosters
    
    @property
    def teams(self):
        standings = self.standings
        teams = standings[['team_id','team_name']].drop_duplicates()
        teams['league_id'] = self.league_id
        teams['season_id'] = self.season_id
        teams = teams[['team_id','league_id','season_id']]
        return teams
    
    @property
    def game_ids(self):
        def getGameID(team, lid, season):
            r = session.get(f'https://www.leaguegaming.com/forums/index.php?leaguegaming/league&action=league_page&page=team_page_schedule&teamid={team}&leagueid={lid}&seasonid={season}').text
            soup = BeautifulSoup(r, 'html.parser')
            types = [x.text for x in soup.findAll('h4')]
            matches = soup.findAll('td', {'class':'team_cell'})
            game_ids = [int(link.get('href').split('gameid=')[1].split('&')[0]) for link in soup.findAll('a',href=True) if 'gameid' in link.get('href')]
            names = [match.find('span', {'class':'teamname_s'}).text for match in matches]
            teams_and_ids = [{'team':match.text, 'id':match.find('a')['href'].split('teamid=')[1].split('&')[0]} for match in matches]
            def sub_team_id(x):
                try:
                    for team in teams_and_ids:
                        if x in team['team']:
                            return team['id']
                    return x
                except:
                    return x
            tables = pd.read_html(r)
            mast = []
            current_week = 0
            for table in tables:
                if 'Week' in table.columns[0]:
                    try:
                        week = table.columns[0].split(' ')[1]
                        if current_week < int(week):
                            current_week = int(week)
                            game_type = types[0]
                        else:
                            current_week = int(week)
                            types = types[1:]
                            game_type = types[0]
                        table.columns = ['result','a_team','scoreline','h_team','nan']
                        table = table[['a_team','h_team','scoreline']]
                        def parse_score(x):
                            if len(x) > 2:
                                if x.startswith('vs '):
                                    date = x.split('vs ')[1]
                                    a_score = np.nan
                                    h_score = np.nan
                                    return a_score, h_score, date
                                else:
                                    a_score = x.split(' ')[0]
                                    h_score = x.split(' ')[2]
                                    date = x.split(' ')[3:]
                                    date = ' '.join(date)
                                    return a_score, h_score, date
                            else:
                                a_score = np.nan
                                h_score = np.nan
                                date = np.nan
                                return a_score, h_score, date
                        table['a_team_score'], table['h_team_score'], table['datetime'] = zip(*table['scoreline'].apply(lambda x: parse_score(x)))
                        table['datetime'] = table['datetime'].apply(lambda x: fix_date(x))
                        table['week'] = int(week)
                        table = table[['datetime','week','a_team','a_team_score','h_team_score','h_team','datetime']]
                        table['game_type'] = game_type
                        mast.append(table)
                    except UnicodeDecodeError:
                        print('error', table)
                        pass
            if mast:
                y = pd.concat(mast)
                y['a_team_id'] = y['a_team'].apply(lambda x: sub_team_id(x))
                y['h_team_id'] = y['h_team'].apply(lambda x: sub_team_id(x))
                y['game_id'] = game_ids
                y = y.dropna(subset=['a_team_id', 'h_team_id'], how='all')
                y['league_id'] = lid
                y['season_id'] = season
                y = y[['game_id','league_id','season_id','game_type','week','a_team_id','h_team_id','datetime']]
                return y
            else:
                return pd.DataFrame()
        teams = self.teams
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(lambda x: getGameID(x[1],x[2],x[3]), teams.itertuples())
        results = pd.concat(results).drop_duplicates(subset=['game_id'], keep='first').sort_values(by=['game_id']).reset_index(drop=True)
        results = results.loc[:, ~results.columns.duplicated()]
        post_res = results.to_json(orient='records')
        session.post(f'{base_url}gameids', json=json.loads(post_res))
        return pd.DataFrame(results)