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
    df_ip = query_ip_by_label(label)
    df_all = query_all()
    global df_temp
    df_temp = df_all[df_all["ip"].isin(df_ip["ip"])]
    result = {"url_count": df_temp.shape[0], "data": []}
    df_temp["domain"] = df_temp["url"].apply(lambda x: x.split("/")[2] if len(x.split("/")) > 2 else x)
    df_group_domain = df_temp.groupby("domain")
    count_list = []
    url_list = []
    for domain, df_group in df_group_domain:
        count_list.append(df_group.shape[0])
        url_list.append(domain)
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
    for index, row in df.iterrows():
        url = row["url"]
        user = row["ip"]
        paths = url.split("/")
        nodes[user] = "person"
        if len(paths) <= 3:
            print("非法url")
        if len(paths) > 5:
            paths = paths[2:5]
        for i in range(len(paths)-1):
            nodes[paths[i]] = "web"
            if links.get(paths[i] + ":" + paths[i+1]) is None:
                links[paths[i] + ":" + paths[i+1]] = 1
            else:
                links[paths[i] + ":" + paths[i+1]] += 1
        nodes[paths[-1]] = "web"
        if links.get(paths[-1] + ":" + user) is None:
            links[paths[-1] + ":" + user] = 1
        else:
            links[paths[-1] + ":" + user] += 1
        # if len(paths) == 3:
        #     if links.get(paths[2] + ":" + user) is None:
        #         links[paths[2] + ":" + user] = 1
        #     else:
        #         links[paths[2] + ":" + user] += 1
        # else:
        #     if nodes.get(paths[3]) is None:
        #         nodes[paths[3]] = "web"
        #         links[paths[2] + ":" + paths[3]] = 1
        #     else:
        #         links[paths[2] + ":" + paths[3]] += 1
        # if len(paths) == 4:
        #     if links.get(paths[3] + ":" + user) is None:
        #         links[paths[3] + ":" + user] = 1
        #     else:
        #         links[paths[3] + ":" + user] += 1
        # else:
        #     if nodes.get(paths[4]) is None:
        #         nodes[paths[4]] = "web"
        #         links[paths[3] + ":" + paths[4]] = 1
        #     else:
        #         links[paths[3] + ":" + paths[4]] += 1
        # if len(paths) >= 5:
        #     if nodes.get(paths[5]) is None:
        #         # nodes[paths[5]] = "web"
        #         # links[paths[4]+":"+paths[5]] = 1
        #         if links.get(paths[4] + ":" + user) is None:
        #             links[paths[4] + ":" + user] = 1
        #         else:
        #             links[paths[4] + ":" + user] += 1
        #     else:
        #         # links[paths[4]+":"+paths[5]] += 1
        #         if links.get(paths[4] + ":" + user) is None:
        #             links[paths[4] + ":" + user] = 1
        #         else:
        #             links[paths[4] + ":" + user] += 1
    print(nodes,links)
    for key, value in nodes.items():
        result.get("nodes").append({"name": key, "status": value})
    for key, value in links.items():
        temp = key.split(":")
        result.get("links").append({"source": temp[0], "target": temp[1], "value": value})
    return_json = json.dumps(result)
    return return_json


@bp.route('/sankey2table',methods=["GET","POST"])
def sankey2table():
    request_data = request.get_json()
    if request_data is None or not isinstance(request_data, list):
        return jsonify({'error':'无效得数据格式！'})
    result = pd.DataFrame()
    for data in request_data:
        ip = data.get('ip')
        url = data.get('url')
        print(ip,type(ip),url,type(url))
        data = query_ip_and_url(ip,url)
        user = query_user_by_ip(ip)
        data = data.merge(user,on='ip')
        if_marking = query_if_marking(ip)
        if if_marking.empty:
            data['marked_or_not'] = '否'
            data['identity'] = None
        else:
            data['marked_or_not'] = '是'
            data['identity'] = if_marking['identity']
        result = pd.concat([result,data])
    ip_access_data = result.groupby('ip')['url'].count().reset_index(name='access_count')
    print(ip_access_data)
    result=result.merge(ip_access_data,on='ip')

    result['access_other'] = result.apply(lambda row:'是' if row['ip_count']<row['access_count'] else "否", axis=1)
    result['url_percentage'] = result['url_percentage'].apply(lambda x:round(x,4))
    print(result.info())
    result.drop(['ip_count','access_count'], axis=1,inplace=True)
    return result.to_dict('records')


@bp.route('/user_marking', methods=["GET","POST"])
def user_marking():
    datas = request.get_json()
    if datas is None or not isinstance(datas, list):
        return jsonify({'error': '无效的数据格式！'})
    for data in datas:
        print(data)
        user_mark = User_marking(data['ip'],data['user'],data['domain'],identity=data['identity'])
        db.session.merge(user_mark)
        db.session.commit()

    return 'success'

@bp.route('/net', methods=["GET","POST"])
def ip_url_net():
    label = request.args.get("label")
    data = query_net()
    df_ip = query_ip_by_label(label)
    df_ip = df_ip.loc[:10]
    data = data[data['ip'].isin(df_ip['ip'])].reset_index(drop=True)
    print(df_ip)
    print(data.info())
    data = data.groupby('ip').apply(lambda x: x.nlargest(10, 'url_count'))
    ip_node_df = data.loc[:, ['ip', 'ip_count']].rename(columns={'ip': 'name', 'ip_count': 'value'}).drop_duplicates()
    url_node_df = data.loc[:, ['url', 'url_count']].rename(columns={'url': 'name', 'url_count': 'value'}).drop_duplicates()

    # ip_value_sum = ip_node_df['value'].sum()
    # print(ip_value_sum)
    ip_node_df['value'] = ip_node_df['value'].apply(lambda x: round(x / 50, 4))

    # url_value_sum = url_node_df['value'].sum()
    # print(url_value_sum)
    url_node_df['value'] = url_node_df['value'].apply(lambda x:round(x/ 50, 4))

    node_df = pd.concat([ip_node_df, url_node_df], ignore_index=True)
    node = node_df.to_dict('records')
    link = data.loc[:, ['ip', 'url', 'count']].rename(columns={'ip': 'source', 'url': 'target', 'count': 'value'})
    value_sum = link['value'].sum()
    print(value_sum)
    link['value'] = link['value'].apply(lambda x: round(x / value_sum, 4))
    result = {'node':node,
              'link':link.to_dict('records')}
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