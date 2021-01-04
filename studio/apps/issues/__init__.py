from flask import Blueprint
issues = Blueprint("issues",__name__,template_folder="templates",static_folder="static")

from studio.apps.issues import views
