from flask.globals import g, request
from flask.helpers import url_for
from flask.templating import render_template
from werkzeug.utils import redirect
from studio.models import db, RouteInterceptors, UserRoles, UserUsers
from .init import console
from studio.utils import and_op


@console.route('/auth')
def auth_get():
    rules = db.session.query(RouteInterceptors.id, RouteInterceptors.startswith, RouteInterceptors.role_bits, RouteInterceptors.description, UserUsers.username)\
        .outerjoin(UserUsers, RouteInterceptors.created_by == UserUsers.id).all()
    roles = UserRoles.query.all()
    for role in roles:
        role.role_bit_bin = bin(role.role_bit)[2:]
    return render_template("auth_manage.html", rules=rules, roles=roles, title="拦截器管理", and_op=and_op)


@console.route('/auth', methods=['POST'])
def auth_add():
    r = RouteInterceptors()
    r.created_by = g.user.id
    r.description = request.values.get('description')
    r.startswith = request.values.get('startswith')
    r.role_bits = 0
    roles = request.values.getlist('roles')
    for _r in roles:
        r.role_bits |= int(_r)
    db.session.add(r)
    db.session.commit()
    return redirect(url_for('console.auth_get'))


@console.route('/auth_update', methods=['POST'])
def auth_update():
    rule = RouteInterceptors.query.filter(
        RouteInterceptors.id == request.values['id']).first()
    rule.role_bits = 0
    roles = request.values.getlist('roles')
    for _r in roles:
        rule.role_bits |= int(_r)
    db.session.commit()
    return redirect(url_for('console.auth_get'))
