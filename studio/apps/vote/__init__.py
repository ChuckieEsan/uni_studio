from flask import Blueprint,current_app
vote = Blueprint("vote",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

from studio.apps.vote import views