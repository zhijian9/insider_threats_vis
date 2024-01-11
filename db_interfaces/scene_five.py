from others import db
import pandas as pd


def query_matrix():
    df = pd.read_sql_query("SELECT source,target,`change` FROM matrix_changes_240110 WHERE `change`=1", db.engine)
    return df

def query_by_target(target):
    df = pd.read_sql_query(f"SELECT source,target,`change` FROM matrix_changes_240110 WHERE target = '{target}' and `change`=1", db.engine)
    return df