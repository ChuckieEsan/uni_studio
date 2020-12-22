from flask import Blueprint
issues = Blueprint("issues",__name__,template_folder="templates",static_folder="static")

from studio.issues import views,admin
