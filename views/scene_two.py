import time

import pandas as pd
from flask import Blueprint
import json
from flask import request
from others.cluster import cluster
from db_interfaces.scene_two import *

bp = Blueprint("scene_two", __name__, url_prefix="/scene_two")


@bp.route("/data4cluster", methods=["GET", "POST"])
def cluster_():
    request_json = request.get_json()
    print(request_json)
    method = request_json.get("method")
    num = request_json.get("num")
    # print(method,num)
    result = {"name": method, "children": []}
    df = cluster(method, num)
    df_group_label = df.groupby("label")
    for label, df_label_group in df_group_label:
        temp = {"name": label}
        size = df_label_group.shape[0]
        temp["size"] = size
        result.get("children").append(temp)
    return_json = json.dumps(result)
    return return_json


@bp.route("/data4table", methods=["GET", "POST"])
def data4table():
    print('----------------')
    label = request.args.get("label")
    print(label)
    s_time = time.time()
    df = query_url_by_label(label)
    total_count = df.shape[0]
    result = {"url_count": total_count, "data": []}
    df_group_domain = df.groupby("domain")
    count_list = []
    url_list = []
    for label, df_group in df_group_domain:
        count_list.append(df_group.shape[0])
        url_list.append("http://" + df_group.iloc[0, 0].split("/")[2])
    ses = pd.Series(count_list)
    ses.sort_values(inplace=True, ascending=False)
    index_list = ses.index.to_list()
    i = 0  # 计数
    for index in index_list:
        if i == 1000:
            break
        temp = {"url": url_list[index], "count": int(ses[index])}
        result.get("data").append(temp)
        i += 1
    return_json = json.dumps(result)
    print(time.time() - s_time)
    return return_json

@bp.route('net')
def ip_url_net():
    data = query_net()
    data = data.loc[(data['ip_count']<50) & (data['url_count']<20)]
    ip_node_df = data.loc[:, ['ip', 'ip_count']].rename(columns={'ip': 'name', 'ip_count': 'value'}).drop_duplicates()
    url_node_df = data.loc[:, ['url', 'url_count']].rename(columns={'url': 'name', 'url_count': 'value'}).drop_duplicates()
    node_df = pd.concat([ip_node_df, url_node_df], ignore_index=True)
    node = node_df.to_dict('records')
    link = data.loc[:, ['ip', 'url', 'count']].rename(columns={'ip': 'source', 'url': 'target', 'count': 'value'}).to_dict('records')
    result = {'node':node,
              'link':link}
    return result