from flask import request
from database import app, Session
from orm_models import GameIDs, TeamStats, PlayerStats, GoalieStats
from sqlalchemy import and_

# Helper Functions
from api_helpers import get_table, get_results, request_GET, request_POST, request_PUT, request_DELETE

# Home Endpoint
@app.route('/api/')
def home():
    return "Welcome to the Spreadsheet API!", 200

# General Endpoint
@app.route('/api/<string:table_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gen_endpoint(table_name):
    table = get_table(table_name)
    if table is None:
        return "Invalid Endpoint", 400
    
    if request.method == 'GET':
        if 'all' in request.args:
            rows = table.query.all()
            return get_results(rows), 200
        
        primary_keys = table.__table__.primary_key.columns.keys()
        columns = table.__table__.columns.keys()

        for param in request.args:
            if param not in columns:
                return f"Invalid Parameter: {param}", 400
        return request_GET(table, request.args, primary_keys, columns)

    if request.method == 'POST': # Modified POST Endpoint that overwrites existing data if present
        data = request.get_json()

        if data is None:
            return "No Data Given", 400
        
        primary_keys = table.__table__.primary_key.columns.keys()
        columns = table.__table__.columns.keys()

        for param in request.args:
            if param not in columns:
                return f"Invalid Parameter: {param}", 400
        
        return request_POST(table, data, primary_keys)
        
    if request.method == 'PUT':
        data = request.get_json()

        if data is None:
            return "No Data Given", 400
        
        primary_keys = table.__table__.primary_key.columns.keys()
        columns = table.__table__.columns.keys()

        for param in request.args:
            if param not in columns:
                return f"Invalid Parameter: {param}", 400
        
        return request_PUT(table, data, primary_keys)
        
    if request.method == 'DELETE':
        primary_keys = table.__table__.primary_key.columns.keys()
        columns = table.__table__.columns.keys()

        for param in request.args:
            if param not in columns:
                return f"Invalid Parameter: {param}", 400
        
        return request_DELETE(table, request.args, primary_keys)

# Joined Stats Endpoint
@app.route('/api/stats/<string:table_name>', methods=['GET'])
def stats_endpoint(table_name):
    accepted_filters = ['game_id','league_id','team_id','opp_id','player_id','season_id','week','game_type']
    session = Session()

    for param in request.args:
        if param not in accepted_filters:
            return f"Invalid Parameter: {param}", 400
    
    if table_name == 'team':
        join_condition = GameIDs.game_id == TeamStats.game_id
        query = session.query(GameIDs, TeamStats).join(TeamStats, join_condition)
    elif table_name == 'player':
        join_condition = GameIDs.game_id == PlayerStats.game_id
        join_condition2 = and_(PlayerStats.game_id == TeamStats.game_id, PlayerStats.team_id == TeamStats.team_id)
        query = session.query(GameIDs, PlayerStats, TeamStats).join(PlayerStats, join_condition).join(TeamStats, join_condition2)
    elif table_name == 'goalie':
        join_condition = GameIDs.game_id == GoalieStats.game_id
        join_condition2 = and_(GoalieStats.game_id == TeamStats.game_id, GoalieStats.team_id == TeamStats.team_id)
        query = session.query(GameIDs, GoalieStats, TeamStats).join(GoalieStats, join_condition).join(TeamStats, join_condition2)
    else:
        return "Invalid Endpoint", 400
    
    for param in request.args:
        try:
            if param == 'game_id':
                query = query.filter(GameIDs.game_id == request.args[param])
            elif param == 'league_id':
                query = query.filter(GameIDs.league_id == request.args[param])
            elif param == 'team_id':
                query = query.filter(TeamStats.team_id == request.args[param])
            elif param == 'opp_id':
                query = query.filter(TeamStats.opp_id == request.args[param])
            elif param == 'player_id':
                query = query.filter(PlayerStats.player_id == request.args[param])
            elif param == 'season_id':
                query = query.filter(GameIDs.season_id == request.args[param])
            elif param == 'week':
                query = query.filter(GameIDs.week == request.args[param])
            elif param == 'game_type':
                query = query.filter(GameIDs.game_type == request.args[param])
        except:
            pass
    rows = query.all()
    return get_results(rows), 200

if __name__ == '__main__':
    app.run(debug=True)
    

        
        
    


