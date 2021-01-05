from flask import Blueprint,current_app,render_template
from studio.interceptors import session_required,roles_required
console = Blueprint("console",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

@console.route('/')
@session_required('/issues')
@roles_required(['*'])
def console_root():
    return render_template('console_index.html',title='Console')


    
from studio.apps.console import issues,vote