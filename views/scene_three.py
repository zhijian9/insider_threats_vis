from flask import Blueprint,jsonify,request
from db_interfaces.scene_three import *
import re
import json
import time


bp = Blueprint("scene_three", __name__, url_prefix='/scene_three')


df = None
def query_data():
    global df
    if df is None:
        df = query_all()
        #df['url'] = df['url'].apply(lambda x: re.sub(r'/[^/]+$', '', x))
    return df

# noinspection SpellCheckingInspection
@bp.route('/sunbrust',methods=['GET'])
def sunbrust_chart():
    # 获取数据
    sunbrust = query_sunbrust()

    result_list = []
    # 根节点
    result_dict = {'name': 'root'}
    # 用列表来存储单位结构
    result_children =[]
    # 获取单位列表
    ins_list = list(sunbrust['institution'].drop_duplicates())
    # 将每个单位存进单位结构
    for ins in ins_list:
        ins_dict = {'name': ins}
        ins_children =[]
        # 获取该单位下的域列表
        domain_list = list(sunbrust[sunbrust['institution']==ins]['domain_id'].drop_duplicates())
        # 将每个域存进域结构，并将该域下的人员存进域的子节点
        for domain in domain_list:
            domain_dict = {'name': domain}
            domain_children = []
            for user in sunbrust[(sunbrust['institution'] == ins) & (sunbrust['domain_id'] == domain)]['user'].unique():
                domain_children.append({'name':user,'value':1})
            domain_dict['children'] = domain_children
            # 将该域结构存进该单位结构的子节点
            ins_children.append(domain_dict)
        ins_dict['children'] = ins_children
        # 将该单位结构存进根节点root的子节点
        result_children.append(ins_dict)
    result_dict['children'] = result_children
    result_list.append(result_dict)
    # 写进json文件
    with open('root.json','w') as f:
        json.dump(result_list,f)
    return result_list

@bp.route('/sankey',methods=['GET'])
def sankey_diagram():
    # 获取参数
    get_parameters = request.args.to_dict()
    unit = get_parameters.get('unit')
    domain_id = get_parameters.get('domain_id')
    admin = get_parameters.get('admin')
    print(unit,domain_id,admin)
    # 获取数据
    data = query_sunkey(unit)
    data = data[data['values'] > 100]

    # 根据传入参数获取需要的数据
    sankey = data[data['institution']==unit]
    if domain_id:
        sankey = sankey[sankey['domain_id']==domain_id]
    if admin:
        sankey = sankey[sankey['user']==admin]
    # json返回
    result_list = []
    # nodes数据
    nodes = []
    # 获取admin、pc、url列表
    admins = sankey['user'].unique()
    pcs = sankey['pc'].unique()
    urls = sankey['url'].unique()
    # 写进nodes数据
    for user in admins:
        nodes.append({'name': user, 'type': 'user', 'state': 0})
    for pc in pcs:
        nodes.append({'name': pc, 'type': 'pc', 'state': 0})
    for url in urls:
        if sankey[sankey['url']==url]['values'].sum()>300:
            nodes.append({'name': url, 'type': 'url', 'state': 1})
        else:
            nodes.append({'name': url, 'type': 'url', 'state': 0})

    result_dict = {"nodes":nodes}
    # user-pc和pc-url边数据
    links = []
    # 获取user-pc边数据并写进links
    user_pc = sankey.groupby(['user','pc'])['values'].sum().reset_index()
    for index,row in user_pc.iterrows():
        links.append({'source': row['user'], 'target': row['pc'], 'value': row['values']})
    # 将pc-url写入links
    for index,row in sankey.iterrows():
        links.append({'source': row['pc'], 'target': row['url'], 'value': row['values']})

    result_dict['links'] = links
    result_list.append(result_dict)
    with open('sankey.json','w') as f:
        json.dump(result_list,f)
    return  result_list

# 点击pc节点获取相应数据
@bp.route('/clickpc')
def clickPc():
    pc = request.args.get('pc')
    # # 获取访问过该pc的用户
    root = query_pc(pc)
    result = []
    result_dict = {'name':pc}
    result_list = []
    for user in root['user'].unique():
        result_list.append({'name':user})
    result_dict['children'] = result_list
    result.append(result_dict)
    return result

# 点击user获取相应数据
@bp.route('clickuser')
def clickUser():
    user = request.args.get('user')
    # # 获取访问过该user访问过的pc以及在pc上访问的url
    root = query_user(user)
    result = []
    # 根节点为user名称
    result_dict = {'name':user}
    result_children = []
    # 将每个pc作为根节点的孩子节点
    for pc in root['pc'].unique():
        # 将该pc访问的url作为pc的孩子节点
        pc_dict = {'name':pc}
        pc_children = []
        for url in root[root['pc']==pc]['url']:
            pc_children.append({'name':url})
        pc_dict['children'] = pc_children
        result_children.append(pc_dict)
    result_dict['children'] = result_children
    result.append(result_dict)
    return result

# 点击url获取相应数据
@bp.route('clickurl',methods=['GET'])
def clickUrl():
    # 获取传入的url参数
    url = request.args.get('url')
    # # 获取与该url相关的数据
    root = query_url(url)
    result = []
    # 将url作为根节点
    result_dict = {'name':url}
    result_children = []
    # 将访问过该url的pc作为根节点的子节点
    for pc in root['pc'].unique():
        # 将使用过该pc的所有user作为pc的子节点
        pc_dict = {'name':pc}
        pc_children = []
        for index,row in root[root['pc']==pc].iterrows():
            user_dict = {'name':row['user'],'value':row['count']}
            pc_children.append(user_dict)
        pc_dict['children'] = pc_children
        result_children.append(pc_dict)
    result_dict['children'] = result_children
    result.append(result_dict)
    return result

# 点击url获取所有访问过该url的人员比例
@bp.route('user2url')
def user2url():
    # 获取url参数
    url = request.args.get('url')
    # 获取与url相关的数据
    root = query_url(url)
    result = []
    # 将url作为根节点
    result_dict = {'name':url}
    result_children = {}
    # 获取访问过该user的user列表
    userlist =  list(root['user'].unique())
    valuelist = []
    count = root['count'].sum()
    # 将每个user访问该url的次数与该url被访问总次数的比值写进value列表
    for user in userlist:
        valuelist.append(root[root['user']==user]['count'].sum()/count)
    # 子节点添加user列表和value列表
    result_children['name'] = userlist
    result_children['value'] = valuelist
    result_dict['children'] = result_children
    result.append(result_dict)
    return result


