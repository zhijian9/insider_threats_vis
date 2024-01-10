from others import db
import pandas as pd


def query_adjacency_matrix():
    df = pd.read_sql_query("SELECT source,target,`change` FROM adjacency_matrix WHERE `change`=1", db.engine)
    return df

def query_by_target(target):
    df = pd.read_sql_query(f"SELECT source,target,`change` FROM adjacency_matrix WHERE target = '{target}' and `change`=1", db.engine)
    return df