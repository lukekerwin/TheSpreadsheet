from datetime import datetime

def fix_date(string):
    try:
        if string.startswith('Sun'):
            weekday = 6
        elif string.startswith('Mon'):
            weekday = 0
        elif string.startswith('Tue'):
            weekday = 1
        elif string.startswith('Wed'):
            weekday = 2
        elif string.startswith('Thu'):
            weekday = 3
        elif string.startswith('Fri'):
            weekday = 4
        elif string.startswith('Sat'):
            weekday = 5
        else:
            weekday = None
        try:
            date = datetime.strptime(string, '%a %b %d %I:%M%p')
        
            for year in range(2023, 2018, -1):
                date = date.replace(year=year)
                if date.weekday() == weekday:
                    return date.strftime('%Y-%m-%d %H:%M:%S')
            return None
        except:
            return string
    except:
        return string