from others import db
import pandas as pd


def query_all():
    df = pd.read_sql_query("select * from cluster_vector_mean", db.engine)
    return df


def query_url_by_label(label):
    df = pd.read_sql_query(f"select y.url,y.domain,y.path_1 from cluster_result_kmeans x,user_url_vector y where "
                           f"x.user = y.user and x.label={label} limit 1000",
                           db.engine)
    return df
#limit 20000

def query_net():
    df = pd.read_sql_query("select ip,url,count,ip_count,url_count from ip_url_net",db.engine)
    return df
