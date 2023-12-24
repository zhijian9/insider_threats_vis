from flask import Blueprint,jsonify,request
from db_interfaces.scene_four import *
import re
import json
import time

from models.Url_marking import Url_marking
from models.User_marking import User_marking


bp = Blueprint("scene_four", __name__, url_prefix='/scene_four')

@bp.route('/admin2list',methods=["GET"])
def admin2list():
    data = query_admin()
    return data.to_dict('records')

@bp.route('/admin2modify',methods=["GET","POST"])
def admin2modify():
    request_data = request.get_json()
    ip = request_data.get('ip')
    identity = request_data.get('identity')
    print(ip,identity)
    user = User_marking.query.get(ip)
    if identity=='普通用户':
        db.session.delete(user)
    else:
        user.identity = identity
    db.session.commit()

    return 'success'

@bp.route('/ip2url', methods=["GET"])
def ip2url():
    request_data = request.args.to_dict()
    ip = request_data.get('ip')
    domain = request_data.get('domain')
    data = query_urlinfo_by_ip(ip)
    url_marking = query_url_marking()
    data = data.merge(url_marking, on='url', how='left')
    data['domain'] = domain
    data.fillna('无', inplace=True)

    return data.to_dict('records')

@bp.route('/url_marking',methods=["GET","POST"])
def url_marking():
    request_data = request.get_json()
    url = request_data.get('url')
    domain = request_data.get('domain')
    marking = request_data.get('marking')
    print(url,domain,marking)
    url_mark = Url_marking(url,domain,marking)
    db.session.merge(url_mark)
    db.session.commit()

    return 'success'