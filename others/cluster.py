from sklearn.cluster import *
import numpy as np
import pandas as pd
from db_interfaces.scene_two import query_all
from others import db


def cluster(method, num):
    if method == "kmeans":
        return run_km(num)
    elif method == 'spectral':
        return run_sp(num)


def run_km(n_cluster):
    df = query_all()
    df_output = pd.DataFrame(columns=["ip", "f1", "f2", "f3"])
    # 域名集
    domain_list = df["url"].apply(lambda x: x.split("/")[2] if len(x.split("/")) > 2 else x).drop_duplicates().values.tolist()
    df_group_by_ip = df.groupby("ip")
    for ip, df_group in df_group_by_ip:
        sum = 0
        f2 = 0
        f3 = df_group.iloc[0, 2]
        # print(df_group)
        for item in df_group.iterrows():
            # 域名基准
            sum += domain_list.index(item[1]["url"].split("/")[2])
            f2 += item[1]["url_count"]
        df_output.loc[df_output.shape[0]] = [ip, sum / df_group.shape[0], f2, f3]
    dataset = df_output[["f1","f2","f2"]].values
    model = KMeans(n_clusters=n_cluster, random_state=1)
    model.fit(dataset)
    labels = model.labels_
    df_output.insert(df_output.shape[1], 'label', 0)
    df_output["label"] = labels
    df_output[["ip","label"]].to_sql("cluster_result", con=db.engine, if_exists="replace", index=False)
    return df_output

def cal_semi(url_set_1:str,url_set_2:str):
    # 转换整数list
    temp = url_set_1.split(",")
    list1 = []
    for arr in temp:
        list1.append(int(arr[0]))
    temp = url_set_2.split(",")
    list2 = []
    for arr in temp:
        list2.append(int(arr[0]))
    # 分母,计算并集
    temp = []
    temp.extend(list1)
    temp.extend(list2)
    denominator = len(np.unique(temp))
    # 分子，计算交集
    numerator = len(list(set(list1) & set(list2)))
    return numerator/denominator

def cal_affinity_matrix(data:pd.DataFrame):
    l = []
    for cur,row in enumerate(data["url_set"]):
        # print(cur,row)
        temp = []
        for idx,s in enumerate(data["url_set"]):
            if cur == idx:
                temp.append(0)
            else:
                temp.append(cal_semi(row,s))
        l.append(temp)
    output = np.array(l)
    return output

def run_sp(n_cluster):
    df = query_all()
    df_output = pd.DataFrame(columns=["ip", "url_set"])
    # 使用地址作为基准
    url_list = df["url"].drop_duplicates().values.tolist()
    # 使用域名作为基准
    domain_list = df["url"].apply(lambda x: x.split("/")[2] if len(x.split("/")) > 2 else x).drop_duplicates().values.tolist()
    df_group_by_ip = df.groupby("ip")
    for ip, df_group in df_group_by_ip:
        temp = []
        for item in df_group.iterrows():
            # 地址基准
            temp.append(str(url_list.index(item[1]["url"])))
            # 域名基准
            # temp.append(str(domain_list.index(item[1]["url"].split("/")[2])))
        url_set = ",".join(temp)
        df_output.loc[df_output.shape[0]] = [ip, url_set]
    affinity_matrix = cal_affinity_matrix(df_output)
    # 聚类个数
    model = SpectralClustering(affinity='precomputed',n_clusters=n_cluster,random_state=1).fit(affinity_matrix)
    labels = model.labels_
    df_output["label"] = labels
    df_output[["ip","label"]].to_sql("cluster_result", con=db.engine, if_exists="replace", index=False)
    return df_output
