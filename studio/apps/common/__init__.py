from flask import Blueprint,current_app
common = Blueprint("common",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity
