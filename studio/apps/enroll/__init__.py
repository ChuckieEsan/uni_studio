from flask import Blueprint

enroll = Blueprint("enroll",__name__)

@enroll.route('/')
def enroll_index():
    return "this is enroll"