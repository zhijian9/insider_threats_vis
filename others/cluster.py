from sklearn.cluster import *
import pandas as pd
from db_interfaces.scene_two import query_all
from others import db


def cluster(method, num):
    df = query_all()
    dataset = df[["domain", "path1", "path2"]].values
    n_cluster = num
    model = KMeans(n_clusters=n_cluster, random_state=1)
    if method == "kmeans":
        model = KMeans(n_clusters=n_cluster, random_state=1)
    model.fit(dataset)
    labels = model.labels_
    df.insert(df.shape[1], 'label', 0)
    for i, l in enumerate(labels):
        df.loc[i, 'label'] = l
    df.to_sql("cluster_result_kmeans", con=db.engine, if_exists="replace", index=False)
    return df
