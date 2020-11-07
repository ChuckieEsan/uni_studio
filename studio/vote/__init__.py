from flask import Blueprint
vote = Blueprint("vote",__name__,url_prefix='/vote',template_folder='templates',subdomain='www')

from studio.vote import views,admin