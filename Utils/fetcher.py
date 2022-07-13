def dictfetchone(cursor):
    "Return allll rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    row=cursor.fetchone()
    if row is None: return None
    else : return dict(zip(columns, row))

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]