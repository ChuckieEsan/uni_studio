from flask import Blueprint,request,jsonify

udict = Blueprint("udict",__name__,url_prefix="/dict")

@udict.route('/')
def udict_home():
    return '1'