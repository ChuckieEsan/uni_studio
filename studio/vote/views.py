from studio.vote import vote
from studio.models import VoteInfo,VoteCandidates,VoteVotes,db
from studio.utils.captcha_helper import get_captcha_and_img
from studio.decorators import memoize
from flask import url_for,redirect,render_template,request,flash,session,jsonify,Markup
from faker import Faker
from sqlalchemy import func
import json
import time
import random
import datetime
f=Faker(locale='zh_CN')
@vote.route("/")
def root():
    voteinfo_all = VoteInfo.query.all()
    return render_template(
        'vote_index.html',
        info_list=voteinfo_all
        )
@memoize(20)
def get_vote_and_candidate(vote_id:int):
    candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).all()
    candidate_all_sorted = sorted(candidate_all,key=lambda x:x.votes,reverse=True)
    vote_info = VoteInfo.query.filter(VoteInfo.id==vote_id).first_or_404()
    return (candidate_all,candidate_all_sorted,vote_info)

@vote.route('/<int:vote_id>',methods=["GET"])
def vote_page(vote_id):
    #candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).all()
    #vote_info = VoteInfo.query.filter(VoteInfo.id==vote_id).first_or_404()
    t1 = time.time()
    candidate_all,candidate_all_sorted,vote_info = get_vote_and_candidate(vote_id)
    voted = VoteVotes.query.filter(VoteVotes.ip==request.remote_addr).filter(VoteVotes.vote_id==vote_id).first()
    datetime_now = datetime.datetime.now()
    #voted = None #------------------
    if vote_info.start_at > datetime_now or (vote_info.start_at!=vote_info.end_at and vote_info.end_at<datetime_now):
        flash('不在有效的投票时间段内')
        return render_template('vote_result.html',vote_id=vote_id)
    if vote_info.shuffle:
        random.shuffle(candidate_all)
    for c in candidate_all:
        c.description = c.description.replace('<br>','\n')
        c.description = c.description.replace('\r','').replace('\n','<br/>').replace('<br>','<br/>').strip()
        c.description = Markup(c.description)
    session['captcha_time'] = int(time.time())+10*60#10分钟
    session['captcha_str'],captcha_b64 = get_captcha_and_img()
    print('-------------this took {}----------------',time.time()-t1)
    return render_template(
        'vote_vote_page.html',
        candidate_all=candidate_all,
        vote_info=vote_info,
        captcha_b64 =captcha_b64,
        voted = voted,
        candidate_all_sorted=candidate_all_sorted
    )


@memoize(1)
def get_tickets_and_candidates(vote_id:int): 
    candidate_info = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).order_by(VoteCandidates.votes.desc()).limit(5).all()
    vote_tickets = VoteVotes.query.filter(VoteVotes.vote_id==vote_id).filter(VoteVotes.candidate.in_([str(c.id) for c in candidate_info])).all()
    return(vote_tickets,candidate_info)
def tostamp(dt1):
    Unixtime = time.mktime(time.strptime(dt1.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
    return Unixtime

@vote.route('/statistics/<int:vote_id>')
def get_stats(vote_id):
    vote_tickets,candidate_info = get_tickets_and_candidates(vote_id)
    candi_set = set([c.candidate for c in vote_tickets])#set of candidate id
    result = {}
    for c in list(candi_set):
        sum = 0
        for v in vote_tickets:
            if v.candidate == c:
                for _c in candidate_info:
                    if str(_c.id)==str(c):
                        key = _c.title
                        break
                if not result.get(key):
                    result[key] = {}
                sum = sum+1
                result[key][int(tostamp(v.created_at))] = sum#int to enable front-end cmp??
    return jsonify(result)


@vote.route('/captcha',methods=['GET','POST'])
def check_captcha():
    if request.method=='GET':
        session['captcha_str'],captcha_64 = get_captcha_and_img()
        return captcha_64
    if request.method=='POST':
        jsoninput = request.get_json()
        if not session.get('captcha_str'):
            session['captcha_time'] = int(time.time())+10*60 
            session['captcha_str'],captcha_64 = get_captcha_and_img()
            return jsonify({"success":False,"captcha_b64":captcha_64,"data":"无有效验证码"})
        if int(time.time())>session['captcha_time']:
            session['captcha_time'] = int(time.time())+10*60 
            session['captcha_str'],captcha_64 = get_captcha_and_img()
            return jsonify({"success":False,"captcha_b64":captcha_64,"data":"验证码超时"})
        if session['captcha_str']!=jsoninput.get('captcha'):
            session['captcha_time'] = int(time.time())+10*60 
            session['captcha_str'],captcha_64 = get_captcha_and_img()
            return jsonify({"success":False,"captcha_b64":captcha_64,"data":"验证码错误"})
        else:
            return jsonify({"success":True})
    
@vote.route('/<int:vote_id>',methods=["POST"])
def vote_handler(vote_id):
    voted = VoteVotes.query.filter(VoteVotes.ip==request.remote_addr).filter(VoteVotes.vote_id==vote_id).first()
    #voted = None #------------------
    if voted:
        print('voted!!')
        flash("您已投过票！")
        return render_template('vote_result.html',vote_id=vote_id)
    vote_list = request.get_json()
    print(request.form.getlist('candidates'))
    vote_list = request.form.getlist('candidates')
    vs=[]
    id_list = []
    for v in vote_list:
        _v = VoteVotes(
            ip = request.remote_addr,
            candidate = int(v),#['candidate']),
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
    flash('投票成功')
    return render_template('vote_result.html',vote_id=vote_id)

