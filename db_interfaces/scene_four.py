from others import db
import pandas as pd

def query_admin():
    df = pd.read_sql_query("select ip,user,identity from user_marking",db.engine)
    return df