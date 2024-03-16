from flask import Blueprint,jsonify,request
from db_interfaces.scene_four import *
import re
import json
import time




bp = Blueprint("scene_four", __name__, url_prefix='/scene_four')

@bp.route('data2table', methods=['POST','GET'])
def data2table():
    data = query_matrix()
    # data = data.drop_duplicates()
    # count_data = data.groupby('target')['source'].count().reset_index(name='count')
    # data = data.merge(count_data,on='target',how='left')
    return data.to_dict('records')

@bp.route('data2force', methods=['POST','GET'])
def data2force():
    # target = request.args.get('target')
    # print(target)
    # data = query_by_target(target)
    # source_node =  data['source'].unique()
    # nodes = []
    # nodes.append({'id':target,'group':'parent'})
    # for node in source_node:
    #     nodes.append({'id':node,'group':'child'})
    # links = data.groupby(['source','target'])['change'].count().reset_index(name='value').to_dict('records')
    source = request.args.get('source')
    data = query_by_source(source)
    target_node = data['target'].unique()
    nodes = []
    nodes.append({'id':source,'group':'parent'})
    for node in target_node:
        nodes.append({'id':node,'group':'child'})
    links = data.rename(columns={'target_count':'value'}).to_dict('records')
    return jsonify({'nodes':nodes,'links':links})