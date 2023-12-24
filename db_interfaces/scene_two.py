from sqlalchemy import text

from others import db
import pandas as pd


def query_all():
    df = pd.read_sql_query("select ip,url,ip_count,url_count from domain_low_user_access", db.engine)
    return df


def query_ip_by_label(label):
    sql = f"select ip from cluster_result where label={label}"
    df = pd.read_sql_query(sql, db.engine)
    return df
#limit 20000

def query_net():
    df = pd.read_sql_query("select ip,url,count,ip_count,url_count from ip_url_net",db.engine)
    return df


def query_info_by_ip(ip):
    df = pd.read_sql_query(f"select * from ip_url_net where ip = {ip}", db.engine)
    return df

def query_ip_by_url(url):
    df = pd.read_sql_query(f"select ip from ip_url_mapping where url = '{url}'", db.engine)
    return df

def query_ip_and_user():
    df = pd.read_sql_query(f"select ip,user,domain from ip_user_mapping",db.engine)
    return df

def query_user_by_ip(ip):
    df = pd.read_sql_query(f"select ip,user,domain from ip_user_mapping where ip = '{ip}'",db.engine)
    return df

def query_ip_and_url(ip,url):
    sql = text("select ip ,url, count,ip_count, url_percentage from ip_url_net where ip = :ip and url like :url")
    params = {'ip':ip,'url':f'%{url}%'}
    df = pd.read_sql_query(sql,db.engine,params=params)
    # df = pd.read_sql_query(f"select ip,url,count,ip_percentage from ip_url_net where ip = '{ip}' and url = '{url}'", db.engine)
    return df

def query_if_marking(ip):
    df = pd.read_sql_query(f"select * from user_marking where ip = '{ip}'", db.engine)
    return df