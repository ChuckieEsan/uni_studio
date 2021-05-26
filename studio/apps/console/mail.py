from flask.helpers import url_for
from flask.templating import render_template
from studio.apps.console import console
from flask import redirect,request,flash
from studio.utils.send_mail import send_mail
@console.route('/mail')
def mail_index():
    return render_template('mail_index.html')

@console.route('/mail')
def mail_post():
    to = request.values['to']
    content = request.values['content']
    try:
        send_mail(to=to,content=content)
        flash('发送成功')
    except Exception as e:
        flash(e)
    return redirect(url_for('console.mail_index'))

