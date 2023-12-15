from others import db
import pandas as pd

def query_all():
    '''
    获取https的全部数据
    :return:
    '''
    df = pd.read_sql_query("select id,date,user,pc,ip,domain_id,url,institution from test_data", db.engine)
    return df

def query_test():
    df = pd.read_sql_query('select * from https', db.engine)
    return df

def query_sunbrust():
    '''
    获取旭日图数据
    :return:
    '''
    df = pd.read_sql_query(f"select institution,domain_id,user,count from admin",db.engine)
    return df

def query_sunkey(institution):
    '''
    获取桑吉图数据
    :return:
    '''
    df = pd.read_sql_query(f"select user,pc,url,institution,domain_id,`values` from admin_pc_url_values where institution='{institution}'",db.engine)
    return df

def query_url(url):
    '''
    获取该url相关数据
    :return:
    '''
    df = pd.read_sql_query(f"select user,pc,url,count from url_user_count where url = '{url}'",db.engine)
    return df

def query_user(user):
    '''
    获取该user相关数据
    :return:
    '''
    df = pd.read_sql_query(f"select user,pc,url from url_user_count where user = '{user}'",db.engine)
    return df

def query_pc(pc):
    '''
    获取该user相关数据
    :return:
    '''
    df = pd.read_sql_query(f"select user,pc from url_user_count where pc = '{pc}'",db.engine)
    return df

