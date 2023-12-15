from models.User import User
from models.url_user_count import UrlUserCount
from others import db
import pandas as pd
from others.scene_one_utils import time2db_field


def model_to_dict(object):
    return {c.name: getattr(object, c.name) for c in object.__table__.columns}


# 将一组数据转为list
def scalars_to_list(object):
    return [model_to_dict(c) for c in object]


def query_all():
    """
    获取url_user_count全部数据，以dataframe格式返回
    :return:
    """
    df = pd.read_sql_query("select * from url_user_count", db.engine)
    return df


def query_by_time_freq(time, freq):
    """
    根据时间区间、访问频次返回对应数量
    :return:
    """
    df = pd.read_sql_query(f"select count(*) from url_user_count where {time}={freq}", db.engine)
    return int(df.iloc[0, 0])


def query_unit(time, freq):
    """
    统计各单位下访问用户
    :return:
    """
    where_str = ""
    for t in time:
        where_str += f"{freq[0]}<={time2db_field(t)} and {time2db_field(t)}<={freq[1]} and "
    where_str = where_str[0:len(where_str) - 4]
    df = pd.read_sql_query(f"select * from url_user_count where {where_str}", db.engine)
    return df


def query_user(time, freq):
    """
    根据访问时间，访问频次查询用户
    :param time:
    :param freq:
    :return:
    """
    where_str = ""
    where_str += f"{freq[0]}<={time2db_field(time)} and {time2db_field(time)}<={freq[1]}"
    df = pd.read_sql_query(f"select date,user,pc,url from url_user_count where {where_str}", db.engine)
    return df
