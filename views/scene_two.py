import time

import pandas as pd
from flask import Blueprint, jsonify
import json
from flask import request

from models.User_marking import User_marking
from models.Url_marking import Url_marking
from others.cluster import cluster
from others import db
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
    df_ip = query_ip_by_label(label)
    print(df_ip)
    df_all = query_all()
    global df_temp
    df_temp = df_all[df_all["ip"].isin(df_ip["ip"])]
    result = {"url_count": df_temp.shape[0], "data": []}
    df_temp["domain"] = df_temp["url"].apply(lambda x: x.split("/")[2] if len(x.split("/")) > 2 else x)
    df_group_domain = df_temp.groupby("domain")
    count_list = []
    url_list = []
    for label, df_group in df_group_domain:
        count_list.append(df_group.shape[0])
        url_list.append("http://" + label)
    ses = pd.Series(count_list)
    ses.sort_values(inplace=True, ascending=False)
    index_list = ses.index.to_list()
    i = 0  # 计数
    for index in index_list:
        if i == 100:
            break
        temp = {"url": url_list[index], "count": int(ses[index])}
        result.get("data").append(temp)
        i += 1
    return_json = json.dumps(result)
    return return_json
    # s_time = time.time()
    # df = query_url_by_label(label)
    # total_count = df.shape[0]
    # result = {"url_count": total_count, "data": []}
    # df_group_domain = df.groupby("domain")
    # count_list = []
    # url_list = []
    # for label, df_group in df_group_domain:
    #     count_list.append(df_group.shape[0])
    #     url_list.append("http://" + df_group.iloc[0, 0].split("/")[2])
    # ses = pd.Series(count_list)
    # ses.sort_values(inplace=True, ascending=False)
    # index_list = ses.index.to_list()
    # i = 0  # 计数
    # for index in index_list:
    #     if i == 1000:
    #         break
    #     temp = {"url": url_list[index], "count": int(ses[index])}
    #     result.get("data").append(temp)
    #     i += 1
    # return_json = json.dumps(result)
    # print(time.time() - s_time)
    # return return_json

@bp.route("/data4sankey", methods=["GET", "POST"])
def data4sankey():
    domain = request.args.get("domain")
    result = {"nodes": [], "links": []}
    nodes = {}
    links = {}
    print(df_temp)
    df = df_temp[df_temp["domain"] == domain]
    for url in df["url"].values:
        paths = url.split("/")
        nodes[paths[2]] = 1
        if len(paths) > 3:
            if nodes.get(paths[3]) is None:
                nodes[paths[3]] = 2
                links[paths[2]+":"+paths[3]] = 1
            else:
                links[paths[2] + ":" + paths[3]] += 1
        if len(paths) > 4:
            if nodes.get(paths[4]) is None:
                nodes[paths[4]] = 3
                links[paths[3]+":"+paths[4]] = 1
            else:
                links[paths[3] + ":" + paths[4]] += 1
        if len(paths) > 5:
            if nodes.get(paths[5]) is None:
                nodes[paths[5]] = 4
                links[paths[4]+":"+paths[5]] = 1
            else:
                links[paths[4] + ":" + paths[5]] += 1
    for key,value in nodes.items():
        result.get("nodes").append({"name":key,"depth":value})
    for key,value in links.items():
        temp = key.split(":")
        result.get("links").append({"source":temp[0],"target":temp[1],"value":value})
    return_json = json.dumps(result)
    return return_json


@bp.route('/net')
def ip_url_net():
    label = request.args.get("label")
    data = query_net()
    df_ip = query_ip_by_label(label)
    df_ip = df_ip.loc[:10]
    data = data[data['ip'].isin(df_ip['ip'])].reset_index(drop=True)
    print(df_ip)
    print(data.info())
    ip_node_df = data.loc[:, ['ip', 'ip_count']].rename(columns={'ip': 'name', 'ip_count': 'value'}).drop_duplicates()
    url_node_df = data.loc[:, ['url', 'url_count']].rename(columns={'url': 'name', 'url_count': 'value'}).drop_duplicates()
    node_df = pd.concat([ip_node_df, url_node_df], ignore_index=True)
    node = node_df.to_dict('records')
    link = data.loc[:, ['ip', 'url', 'count']].rename(columns={'ip': 'source', 'url': 'target', 'count': 'value'}).to_dict('records')
    result = {'node':node,
              'link':link}
    return result


@bp.route('/net2table')
def net2table():
    ip = request.args.get("ip")
    data = query_info_by_ip(ip)
    return data.to_dict("records")

@bp.route('/url_marking_user', methods=["GET","POST"])
def url_marking_user():
    urls = request.get_json()
    if urls is None or not isinstance(urls, list):
        return jsonify({'error': '无效的数据格式！'})
    for item in urls:
        url = item.get("url")
        print(url)
        df_ip = query_ip_by_url(url)
        data = query_ip_and_user()
        data = data[data['ip'].isin(df_ip['ip'])].reset_index(drop=True)
        for index,row in data.iterrows():
            user_marking = User_marking(row['ip'],row['user'],row['domain'],identity='安全员')
            db.session.merge(user_marking)
            db.session.commit()

    return 'success'


@bp.route("/url_marking", methods=["GET","POST"])
def url_marking():
    url_data = request.args.to_dict()
    print(url_data)
    url_marking = Url_marking(url_data['url'],url_data['domain'],url_data['marking'])
    db.session.merge(url_marking)
    db.session.commit()
    # result = update_url_marking(url_data)
    print(url_marking)
    return 'success'