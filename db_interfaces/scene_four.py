from others import db
import pandas as pd

def query_admin():
    df = pd.read_sql_query("select ip,user,identity,domain from user_marking",db.engine)
    return df

def query_urlinfo_by_ip(ip):
    df = pd.read_sql_query(f"select * from ip_url_net where ip = {ip}", db.engine)
    return df

def query_url_marking():
    df = pd.read_sql_query(f"select url,marking,domain from url_marking", db.engine)
    return df