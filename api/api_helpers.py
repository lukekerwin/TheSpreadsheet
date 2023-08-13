from orm_models import GoalieStats, PlayerStats, TeamStats, GameIDs, League, Player, Team, Roster, Sos, Gsos, Tsos, Pwar, Gwar, Twar, Wrosters
from orm_models import db
import json
from sqlalchemy import text


# Helper Functions
def get_table(table_name):
    if table_name == 'goaliestats':
        return GoalieStats
    elif table_name == 'playerstats':
        return PlayerStats
    elif table_name == 'teamstats':
        return TeamStats
    elif table_name == 'gameids':
        return GameIDs
    elif table_name == 'leagueinfo':
        return League
    elif table_name == 'playerinfo':
        return Player
    elif table_name == 'teaminfo':
        return Team
    elif table_name == 'rosters':
        return Roster
    elif table_name == 'sos':
        return Sos
    elif table_name == 'gsos':
        return Gsos
    elif table_name == 'tsos':
        return Tsos
    elif table_name == 'pwar':
        return Pwar
    elif table_name == 'gwar':
        return Gwar
    elif table_name == 'twar':
        return Twar
    elif table_name == 'wrosters':
        return Wrosters
    else:
        return None
    
def get_len(row):
    length = 0
    for r in row:
        length += 1
    return length
    
def get_results(rows):
    output = []
    for row in rows:
        try:
            data = {}
            for column in range(get_len(row)):
                dic = row[column].__dict__
                if '_sa_instance_state' in dic:
                    del dic['_sa_instance_state']
                data.update(dic)
            output.append(data)
        except:
            data = row.__dict__
            if '_sa_instance_state' in data:
                del data['_sa_instance_state']
            output.append(data)
    return output

def get_query_filters(args):
    if isinstance(args, str):
        query = json.loads(args)
    
    if isinstance(args, dict):
        if args:
            filters = []
            for key, value in args.items():
                if value:
                    filters.append(str(key) + "='" + str(value) + "'")
            return " AND ".join(filters)
        else:
            return ""
    
    if isinstance(args, list):
        if args:
            filters = []
            for arg in args:
                if isinstance(arg, dict):
                    for key, value in arg.items():
                        if value:
                            filters.append(str(key) + "='" + str(value) + "'")
            return " AND ".join(filters)
        else:
            return ""
        
def updated_row(table, record):
    table_name = table.__tablename__
    query = f'REPLACE INTO {table_name} '
    columns = "("
    values = "("
    params = {}

    for key, value in record.items():
        columns += f"{key}, "
        values += f":{key}, "
        params[key] = value
    
    columns = columns[:-2] + ")"
    values = values[:-2] + ")"

    query += columns + " VALUES " + values
    return query, params

def request_GET(table, args, primary_keys, columns):
    pk_args = {key: args[key] for key in args if key in primary_keys}
    non_pk_args = {key: args[key] for key in args if key in columns}

    query_filters = get_query_filters(pk_args)

    if query_filters:
        rows = table.query.filter(text(query_filters)).all()
        return get_results(rows), 200
    else:
        query_filters = get_query_filters(non_pk_args)
        if query_filters:
            rows = table.query.filter(text(query_filters)).all()
            return get_results(rows), 200
        else:
            return "No Parameters Given", 400
        
def request_POST(table, data, primary_keys):
    pk_args = {key: data[key] for key in data if key in primary_keys}

    query_filters = get_query_filters(pk_args)

    if isinstance(data, str):
        data = json.loads(data)
    
    if not isinstance(data, list):
        data = [data]
    
    for record in data:
        query_filters = get_query_filters([{key: record[key] for key in record if key in primary_keys}])
        result = table.query.filter(text(query_filters)).first()
        if result:
            query, params = updated_row(table, record)
            db.session.execute(text(query).bindparams(**params))
        else:
            table.insert(record)
    db.session.commit()
    return "Success", 200     

def request_PUT(table, data, primary_keys):
    pk_args = {key: data[key] for key in data if key in primary_keys}

    query_filters = get_query_filters(pk_args)

    if isinstance(data, str):
        data = json.loads(data)
    
    if not isinstance(data, list):
        data = [data]
    
    for record in data:
        query_filters = get_query_filters([{key: record[key] for key in record if key in primary_keys}])
        if query_filters:
            rows = table.query.filter(text(query_filters)).update(record, synchronize_session=False)
        
    db.session.commit()
    return "Success", 200

def request_DELETE(table, args, primary_keys):
    pk_args = {key: args[key] for key in args if key in primary_keys}

    query_filters = get_query_filters(pk_args)

    if query_filters:
        rows = table.query.filter(text(query_filters)).delete(synchronize_session=False)
        db.session.commit()
        return "Success", 200
    else:
        return "No Parameters Given", 400
        

        
        
    