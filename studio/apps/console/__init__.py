from flask import Blueprint,current_app,render_template,jsonify,request,g
import docker
import re
import time
import os
from studio.models import db,UserRoles,RouteInterceptors
console = Blueprint("console",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

@console.route('/')
def console_root():
    roles = UserRoles.query.filter(UserRoles.delete==False).all()
    routes = RouteInterceptors.query.filter(RouteInterceptors.delete==False).all()
    user_role = g.user.role_bits or 2

    valid_routes = [r for r in routes if user_role & r.role_bits or user_role==1]

    valid_roles = [r for r in roles if user_role & r.role_bit or user_role==1]

    return render_template('console_index.html',\
        title='Console',roles=valid_roles,routes=valid_routes)


@console.route('/tskey',methods=['GET'])
def get_tslog():
    client = docker.from_env()
    cli_lists = client.containers.list()
    for cli in cli_lists:
        if str(cli.image)=="<Image: 'teamspeak:latest'>":
            container = client.containers.get(cli.id)
            log = str(container.logs())
            key = re.findall(r'token=(.*)\\',log)
            n = key[0].find('\\n')

            if len(key)>0:
                return key[0][:n]
            else:
                break
    return 'not found'

@console.route('/livelog',methods=['GET'])
def get_livelog():
    return current_app.live_log.read()

@console.route('/log',methods=['GET'])
def show_livelog():
    return render_template('console_livelog.html')

from studio.apps.console import issues,vote,user,vol_time,crud