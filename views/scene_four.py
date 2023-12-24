from flask import Blueprint,jsonify,request
from db_interfaces.scene_four import *
import re
import json
import time
from models.User_marking import User_marking


bp = Blueprint("scene_four", __name__, url_prefix='/scene_four')

@bp.route('/admin2list',methods=["GET"])
def admin2list():
    data = query_admin()
    return data.to_dict('records')

@bp.route('/admin2modify',methods=["GET","POST"])
def admin2modify():
    request_data = request.args.to_dict()
    ip = request_data.get('ip')
    identity = request_data.get('identity')
    print(ip,identity)
    user = User_marking.query.get(ip)
    user.identity = identity
    db.session.commit()

    return 'success'