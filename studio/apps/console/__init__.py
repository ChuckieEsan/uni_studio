from flask import Blueprint,current_app,render_template,jsonify,request
from studio.interceptors import session_required,roles_required
from studio.utils.rules_helper import get_rules,add_rule,remove_rule
console = Blueprint("console",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

@console.route('/')
@session_required('/console/')
@roles_required(['*'])
def console_root():
    return render_template('console_index.html',title='Console')

@console.route('/rules',methods=['GET','POST','DELETE'])
@session_required('/console/')
@roles_required(['super_admin'])
def rules_handler():
    if request.method=='GET':
        return jsonify(list(get_rules()))
    elif request.method=='DELETE':
        remove_rule(request.values.get('rule'))
        return jsonify({'success':True})
    elif request.method=='POST':
        add_rule(request.values.get('rule'))
        return jsonify({'success':True})


from studio.apps.console import issues,vote