from flask import Blueprint, render_template, request, make_response, current_app
from studio.models import IssuesIssues, db
import random
h5 = Blueprint("h5", __name__, template_folder="templates", static_folder="static")


@h5.route('/72years', methods=['GET', 'POST'])
def celeb_72_form():
    return render_template('dut72years_form.html')


@h5.route('/72years/card', methods=['GET', 'POST'])
def celeb_72_card():
    data = request.values.to_dict()
    current_app.logger.info(data)
    back_images = ['orange.png', 'blue.png', 'gold.png', 'green.png', 'purple.png', 'red.png', 'silver.png']
    if data['wish'] == 'others':
        data['wish'] = data['wish_other']
    image = random.sample(back_images, 1)

    res = make_response(render_template('dut72years_card.html', data=data, image=image))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Method'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res
    # return


@h5.route('/cert', methods=['GET', 'POST'])
def cert_form():
    return render_template('cert_form.html')


@h5.route('/cert/card', methods=['GET', 'POST'])
def cert_card():
    data = request.values.to_dict()
    issue = IssuesIssues(ip=request.remote_addr,
                         url='www.dutbit.com/h5/cert',
                         type='专属证书',
                         contact='00',
                         name=data['name'],
                         stu_id=data['stu_num'],
                         content=data['department'],
                         user_id=None)
    db.session.add(issue)
    db.session.commit()

    res = make_response(render_template('cert_card.html', data=data))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Method'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res
