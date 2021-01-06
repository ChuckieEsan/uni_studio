from flask import Blueprint,abort
tests = Blueprint("test",__name__)

@tests.route("/hello")
def helo():
    abort(404)
    return "world"