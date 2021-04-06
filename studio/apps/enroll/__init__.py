from flask import Blueprint

enroll = Blueprint("enroll",__name__)

@enroll.route('/')
def enroll_home():
    return "this is enroll"