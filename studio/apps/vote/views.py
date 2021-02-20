from studio.apps.vote import vote
from studio.models import VoteInfo,VoteCandidates,VoteVotes,db
from studio.utils.captcha_helper import get_captcha_and_img
from studio.cache import memoize
from studio.interceptors import set_captcha,validate_captcha
from flask import url_for,redirect,render_template,request,flash,session,jsonify,Markup,send_file
from flask import current_app
from faker import Faker
from sqlalchemy import func
import json
import time
import random
import datetime
import csv
import codecs
import os
f=Faker(locale='zh_CN')
@vote.route("/")
def root():
    voteinfo_all = VoteInfo.query.all()
    return render_template(
        'vote_index.html',
        info_list=voteinfo_all,
        title="投票列表"
        )
#@memoize(20)
def get_vote_and_candidate(vote_id:int):
    candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).all()
    candidate_all_sorted = sorted(candidate_all,key=lambda x:x.votes,reverse=True)
    vote_info = VoteInfo.query.filter(VoteInfo.id==vote_id).first_or_404()
    return (candidate_all,candidate_all_sorted,vote_info)


@vote.route('/<int:vote_id>',methods=["GET"])
def vote_page(vote_id):
    t1 = time.time()
    candidate_all,candidate_all_sorted,vote_info = get_vote_and_candidate(vote_id)
    voted = VoteVotes.query.filter(VoteVotes.ip==request.remote_addr).filter(VoteVotes.vote_id==vote_id).first()
    datetime_now = datetime.datetime.now()
    if vote_info.start_at > datetime_now or (vote_info.start_at!=vote_info.end_at and vote_info.end_at<datetime_now):
        flash('不在有效的投票时间段内')
        return render_template('vote_result.html',vote_id=vote_id,title="投票结果")
    if vote_info.shuffle:
        random.shuffle(candidate_all)
    for c in candidate_all:
        c.description = c.description.replace('<br>','\n')
        c.description = c.description.replace('\r','').replace('\n','<br/>').replace('<br>','<br/>').strip()
        c.description = Markup(c.description)
    session['captcha_time'] = int(time.time())+10*60#10分钟
    session['captcha_str'],captcha_b64 = get_captcha_and_img()
    current_app.logger.debug('timing-of-vote_page:'+str(time.time()-t1))
    return render_template(
        'vote_vote_page.html',
        candidate_all=candidate_all,
        vote_info=vote_info,
        captcha_b64 =captcha_b64,
        voted = voted,
        candidate_all_sorted=candidate_all_sorted,
        echarts = True
    )


def get_tickets_and_candidates(vote_id:int,lim=5): 
    candidate_info = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).order_by(VoteCandidates.votes.desc()).limit(lim).all()
    vote_tickets = VoteVotes.query.filter(VoteVotes.vote_id==vote_id).all()
    return(vote_tickets,candidate_info)
def tostamp(dt1):
    Unixtime = time.mktime(time.strptime(dt1.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
    return Unixtime



@vote.route('/statistics/<int:vote_id>')
def get_vote_stats(vote_id):
    lim = 5 if request.values.get('lim') is None else int(request.values.get('lim'))
    res = {}
    vote_tickets,candidate_info = get_tickets_and_candidates(vote_id,lim=lim)
    for c in candidate_info:
        key = str(c.id)+"-"+c.title
        res[key] = []
        for v in vote_tickets:
            if v.candidate == c.id:
                res[key].append(int(tostamp(v.created_at)))
    return jsonify(res)
@vote.route('/stats/<int:vote_id>')
def show_stats(vote_id):
    return render_template('vote_stats.html',vote_id=vote_id)

@vote.route('/getcsv/<int:vote_id>')
def getcsv(vote_id):
    res = {}
    data = {}
    head = []
    vote_tickets,candidate_info = get_tickets_and_candidates(vote_id,lim=80)
    for c in candidate_info:
        key = str(c.id)+"-"+c.title
        res[key] = []
        for v in vote_tickets:
            if v.candidate == c.id:
                res[key].append(int(tostamp(v.created_at)))
    _start = 1607601600
    _step = 600 if request.values.get('step') is None else int(request.values.get('step'))
    _end = 1608136800
    head.append('姓名')
    for i in range(0,int((_end-_start)/600)):
        timeArray = time.localtime(_start+_step*i)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        head.append(otherStyleTime)
    names = list(res.keys())
    for i in range(len(names)):
        data[names[i]] = []
        now = _start
        step = _step
        end = _end
        while now <= end:
            count = 0
            for j in range(len(res[names[i]])):
                if res[names[i]][j]<now:
                    count = count + 1
            data[names[i]].append(count)
            now = now + step
    fname = os.path.join(os.getcwd(),'studio','apps','vote','static','csv',\
    'vote_'+str(vote_id)+'_'+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))+'.csv')
    with codecs.open(fname, 'wb', "gbk") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(head)
        for k in data:
            csv_writer.writerow([k]+data[k])
    return send_file(fname,as_attachment=True,attachment_filename=fname)


@vote.route('/<int:vote_id>',methods=["POST"])
@validate_captcha
def vote_handler(vote_id):
    voted = VoteVotes.query.filter(VoteVotes.ip==request.remote_addr).filter(VoteVotes.vote_id==vote_id).first()
    if voted:
        current_app.logger.warn('vote_attempt:'+request.remote_addr)
        return jsonify({"success":False,"details":"您已投过票"})
    vote_list = request.get_json()
    current_app.logger.debug('candidates:'+str(request.form.getlist('candidates')))
    vote_list = request.form.getlist('candidates')
    vs=[]
    id_list = []
    for v in vote_list:
        _v = VoteVotes(
            ip = request.remote_addr,
            candidate = int(v),
            vote_id = vote_id
        )
        vs.append(_v)
        id_list.append(_v.candidate)
    db.session.add_all(vs)
    VoteCandidates.query.filter(VoteCandidates.id.in_(id_list)).update({
        VoteCandidates.votes:VoteCandidates.votes+1
    },synchronize_session=False)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('vote.vote_result_handler',vote_id=vote_id))


@vote.route('/result/<int:vote_id>',methods=['GET'])
def vote_result_handler(vote_id):
    flash("投票成功")
    return render_template('vote_result.html',vote_id=vote_id,title="投票结果")