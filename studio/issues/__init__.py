from flask import Blueprint
issues = Blueprint("issues",__name__,template_folder="templates")

from studio.issues import views,admin
