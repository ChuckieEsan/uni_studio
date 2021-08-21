from flask.globals import request
from flask.helpers import url_for
from werkzeug.utils import redirect
from .init import console
from flask import render_template, g
from studio.models.enroll import db, EnrollCandidates, EnrollForms


@console.route('/enroll')
def enroll_console():
    info_list = EnrollForms.query.filter(
        EnrollForms.created_by == g.user.id).all()
    return render_template('enroll_admin_index.html', info_list=info_list)


@console.route('/enroll', methods=['POST'])
def enroll_form_add():
    f = EnrollForms(request.get_data())
    db.session.add(f)
    db.session.commit()
    return redirect(url_for('console.enroll_console'))
