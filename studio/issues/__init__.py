from flask import Blueprint
issues = Blueprint("issues",__name__,url_prefix="/issues",template_folder="templates")

from studio.issues import views,admin