from flask import Blueprint, render_template, request, jsonify, g, redirect, Response, current_app
from flask.helpers import make_response, url_for, flash
from studio.models import db, UserUsers
from studio.utils.send_mail import send_mail
from studio.utils.captcha_helper import getcaptcha
users = Blueprint("users", __name__,
                  template_folder="templates", static_folder="static")


@users.route('/')
def users_entrypoint():
    return render_template('users_index.html', title="DUTBIT SSO")


@users.route('/register', methods=['POST'])
def users_register():
    user = UserUsers(kwargs=request.get_json())
    user.role_bits = 2
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True})


@users.route('/login', methods=['POST'])
def users_login():
    data = request.get_json()
    user = UserUsers.query.filter(UserUsers.email == str(data.get('email')).strip())\
        .filter(UserUsers.password == str(data.get('password')).strip()).first()
    if user:
        info = {'id': user.id}
        resp: Response = jsonify({"success": True})
        token = current_app.tjwss.dumps(info).decode()
        resp.set_cookie('token', token, max_age=current_app.config['TOKEN_EXPIRES_IN'],
                        domain=current_app.config['SERVER_NAME'], secure=True, httponly=True)
        return resp
    return jsonify({"success": False, "details": "用户名或密码错误"})


@users.route('/iforgot', methods=['GET'])
def users_password_step1():
    email = request.values.get('email')
    user = UserUsers.query\
        .filter(UserUsers.email == str(email).strip()).first()
    if not user:
        if email:
            flash('无效的邮箱')
        email = None
    else:
        info = {'id': user.id}
        token = current_app.tjwss.dumps(info).decode()
        email_html = """<h1>dutbit-密码重置</h1>
        <a href="http://{}{}?token={}">重置链接</a>
        """.format(current_app.config['SERVER_NAME'], url_for('users.users_password_step2'), token)
        send_mail(to=user.email, content=email_html, subject='dutbit-密码重置')
    if current_app.debug and user:
        return render_template('users_password_step1.html', email=email, email_html=email_html)
    return render_template('users_password_step1.html', email=email)


@users.route('/iforgot/validate', methods=['GET'])
def users_password_step2():
    token = request.values.get('token')
    try:
        current_app.tjwss.loads(token)
    except:
        flash('无效token')
        return redirect(url_for('users.users_password_step1'))
    return render_template('users_password_step2.html', token=token)


@users.route('/iforgot/set', methods=['POST'])
def users_password_set():
    token = request.values.get('token')
    data = current_app.tjwss.loads(token)
    uid = data['id']
    new_password = request.values.get('password')
    UserUsers.query.filter(UserUsers.id == uid).update(
        {UserUsers.password: new_password})
    db.session.commit()
    return redirect(url_for('users.users_entrypoint'))


@users.route('/confirm')
def users_confirm_index():
    if not g.user:
        return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
    if g.user.confirmed:
        return redirect(url_for('console.console_root'))
    return render_template('users_confirm.html')



@users.route('/confirm', methods=['POST'])
def users_confirm_post():
    if not g.user:
        return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
    if request.values['code'] != g.user.validation_code:
        flash('验证码无效')
        return redirect(url_for('users.users_confirm_index'))
    UserUsers.query.filter(UserUsers.id == g.user.id).update({
        UserUsers.confirmed: True,
        UserUsers.validation_code: ''
    })
    db.session.commit()
    flash('验证完成，3秒后跳转')
    return render_template('users_confirm.html',confirmed=True)


@users.route('/logout')
def users_logout():
    response = make_response(redirect(url_for('users.users_entrypoint')))
    response.set_cookie('token', '', max_age=1,
                        domain=current_app.config['SERVER_NAME'], secure=True, httponly=True)
    return response
