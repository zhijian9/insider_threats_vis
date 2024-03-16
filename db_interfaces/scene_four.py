from others import db
import pandas as pd

def query_matrix():
    df = pd.read_sql_query("SELECT source,target,target_count FROM matrix_changes WHERE `change`=1", db.engine)
    return df

def query_by_source(source):
    df = pd.read_sql_query(f"SELECT source,target,target_count FROM matrix_changes WHERE source = '{source}'", db.engine)
    return df