import pandas as pd
from flask import Blueprint
from db_interfaces.scene_one import *
import json
from flask import request
from others.scene_one_utils import *

bp = Blueprint("scene_one", __name__, url_prefix="/scene_one")


@bp.route("/main")
def main():
    """
    场景一默认请求，返回频次，访问人数
    :return:
    """
    df = query_all()
    result = {
        "url_count": {
            "midnight": [],
            "morning": [],
            "afternoon": [],
            "evening": [],
        },
        "user_count": {
            "midnight": 0,
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
        }
    }
    url_keys = result["url_count"].keys()
    user_keys = list(result["user_count"].keys())
    for i in range(50):
        temp = []
        temp.append(df[df["one"] == i + 1].shape[0])
        temp.append(df[df["two"] == i + 1].shape[0])
        temp.append(df[df["three"] == i + 1].shape[0])
        temp.append(df[df["four"] == i + 1].shape[0])
        for index, key in enumerate(url_keys):
            result.get("url_count")[key].append(temp[index])
        temp.clear()
    result.get("user_count")[user_keys[0]] = int(df[df["one"] > 0]["user"].drop_duplicates().shape[0])
    result.get("user_count")[user_keys[1]] = int(df[df["two"] > 0]["user"].drop_duplicates().shape[0])
    result.get("user_count")[user_keys[2]] = int(df[df["three"] > 0]["user"].drop_duplicates().shape[0])
    result.get("user_count")[user_keys[3]] = int(df[df["four"] > 0]["user"].drop_duplicates().shape[0])
    return_json = json.dumps(result)
    return return_json


@bp.route("/data4parallel", methods=["POST", "GET"])
def data4parallel():
    # 频次区间，时间区间
    result = {}
    request_json = request.get_json()
    arg_freq = request_json.get("frequency")
    arg_time = request_json.get("time")
    freq = trans_freq(arg_freq)
    time = arg_time.split(";")
    result["parallel_data"] = {}
    result["unit_data"] = []
    for i, t in enumerate(time):
        result.get("parallel_data")[time2json_field(t)] = []
    fields = list(result.get("parallel_data").keys())
    # 构建返回数据
    for index, t in enumerate(time):
        for i in range(freq[0], freq[1] + 1, 1):
            count = query_by_time_freq(time2db_field(t), i)
            result.get("parallel_data").get(fields[index]).append([t, i, count])
    df = query_unit(time, freq)
    df_group_domain = df.groupby("domain_id")
    for label, df_group in df_group_domain:
        # 按所添加
        temp = {"name": label, "children": []}
        sub_group = df_group.groupby("user")
        for user, df_user_group in sub_group:
            sub_temp = {"name": user, "children": []}
            # for index, row in df_user_group.iterrows():
            #     sub_temp["children"].append({"name": row["url"]})
            temp["children"].append(sub_temp)
        result.get("unit_data").append(temp)
    return_json = json.dumps(result)
    return return_json


@bp.route("/data4unit", methods=["POST", "GET"])
def data4unit():
    result = {"unit_data": [],"table_data":[]}
    request_json = request.get_json()
    # print(type(request_json))
    arg_df = pd.DataFrame(request_json)
    time_df = arg_df.iloc[:, 0]
    arg_df = arg_df.iloc[:, 1]
    time_df.drop_duplicates(inplace=True)
    time = time_df.to_list()
    freq = [int(arg_df.min()), int(arg_df.max())]
    # 构建返回数据
    df = query_unit(time, freq)
    print(df.info())
    print(df)
    # 按单位分组
    df_group_domain = df.groupby(["domain_id"])
    for label, df_group in df_group_domain:
        print(label)
        temp = {"name": label, "size": df_group["user"].drop_duplicates().shape[0], "children": []}
        df_user = df_group.groupby("user")
        for user, df_group_user in df_user:
            temp.get("children").append({"name": user})
        result.get("unit_data").append(temp)
    for t in time:
        df = query_user(t, freq)
        for row_data in df.itertuples():
            temp = {"date": row_data[1],
                    "user": row_data[2],
                    "pc": row_data[3],
                    "url": row_data[4]}
            result.get("table_data").append(temp)
    return_json = json.dumps(result)
    return return_json


@bp.route("/data4table", methods=["POST", "GET"])
def data4table():
    result = {"data": []}
    request_json = request.get_json()
    arg_freq = request_json.get("frequency")
    arg_time = request_json.get("time")
    freq = trans_freq(arg_freq)
    df = query_user(arg_time, freq)
    for row_data in df.itertuples():
        temp = {"date": row_data[1],
                "user": row_data[2],
                "pc": row_data[3],
                "url": row_data[4]}
        result.get("data").append(temp)
    return_json = json.dumps(result)
    return return_json
