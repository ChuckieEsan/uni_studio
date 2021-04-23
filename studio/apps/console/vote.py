from studio.apps.console import console as vote
from studio.utils.time_helper import timestamp_to_datetime
from studio.utils.hash_helper import md5
from studio.models import VoteInfo,VoteCandidates,VoteVotes,db
from flask import url_for,redirect,abort,render_template,request,Markup,g
from faker import Faker
import time
import os
f=Faker(locale='zh_CN')
@vote.route('/vote',methods=["GET"])#投票管理大厅，能看所有投票
def admin_votes_show():
    voteinfo_all = VoteInfo.query.filter().all()
    return render_template(
        'vote_admin_index.html',
        info_list=voteinfo_all
        )
        
@vote.route('/vote/shuffle/<int:vote_id>')
def toggle_shuffle(vote_id):
    vote_info = VoteInfo.query.filter(VoteInfo.id==vote_id).first_or_404()
    vote_info.shuffle = not vote_info.shuffle
    try:
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect(url_for('vote.admin_vote_page',vote_id=vote_id))

@vote.route('/vote',methods=["POST"])#新建投票接口
def admin_votes_add():
    #new_vote = request.get_json()
    new_vote = request.form
    v = VoteInfo(
        title=new_vote.get("title"),
        subtitle=new_vote.get("subtitle"),
        description=new_vote.get("description"),
        image=new_vote.get("image"),
        start_at=timestamp_to_datetime(new_vote.get("start_at")),
        end_at=timestamp_to_datetime(new_vote.get("end_at")),
        vote_min=new_vote.get("vote_min"),
        vote_max=new_vote.get("vote_max"),
        admin=g.user.id
    )
    #VoteInfo.add(v)
    db.session.add(v)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('vote.admin_votes_show'))

@vote.route('/vote/<int:vote_id>',methods=["GET"])
def admin_vote_page(vote_id):
    candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).all()
    vote_info = VoteInfo.query.filter(VoteInfo.id==vote_id).first_or_404()
    for c in candidate_all:
        c.description = Markup(c.description)
    return render_template(
        'vote_admin_vote_page.html',
        candidate_all=candidate_all,
        vote_info=vote_info,
    )


@vote.route('/vote/<int:vote_id>/candidates',methods=["POST"])
def candidate_add(vote_id):
    new_candidate = request.form
    #print(request.form)
    _file = request.files.get('image')
    file_suffix = _file.filename.split('.')[-1]
    if file_suffix not in ['png','PNG','jpg','JPG','JPEG','jpeg','mp3']:
        return abort(500)
    print(os.getcwd())
    access_dir = '/vote/static/uploads/'+md5(str(time.time())+str(_file.filename))+'.'+file_suffix
    path = os.getcwd()+'/studio'+access_dir
    try:
        _file.save(path)
    except Exception as e:
        print(e)
        return abort(500)
    _des = new_candidate.get('description').strip()#.replace('\n','<br>')
    c = VoteCandidates(
        title=new_candidate.get("title"),#姓名
        subtitle=new_candidate.get("subtitle"),#所在社区
        description=_des,#new_candidate.get("description"),#周记
        vote_id=vote_id,
        action_at = new_candidate.get('action_at'),#时间
        image=access_dir
    )
    db.session.add(c)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return redirect(url_for('vote.admin_vote_page',vote_id=vote_id))



@vote.route('/vote/<int:vote_id>/candidates/drop/<int:candidate_id>',methods=["GET"])
@vote.route('/vote/candidates/<candidate_id>',methods=["DELETE"])
def candidate_del(vote_id,candidate_id):
    VoteCandidates.query.filter(VoteCandidates.id==candidate_id).delete()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('console.admin_vote_page',vote_id=vote_id))


@vote.route('/vote/drop/<vote_id>',methods=["GET"])
@vote.route('/vote/<vote_id>',methods=["DELETE"])
def votes_del(vote_id):
    VoteInfo.query.filter(VoteInfo.id==vote_id).delete()
    #delete candidates and corresponding vote tickets?
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('console.admin_votes_show'))

@vote.route('/vote/ballots/<vote_id>',methods=["GET"])
def votes_details_show(vote_id):
    all = VoteVotes.query.filter(VoteVotes.id==vote_id).all()
    return render_template('vote_admin_votes.html',votes_all=all)


@vote.route('/vote/populate/<vote_id>')
def populate_id(vote_id):
    cs = []
    for i in range(0,5):
        c = VoteCandidates(
            title=f.name(),
            subtitle=f.company_prefix(),
            description=f.paragraph(),
            vote_id=vote_id
            )
        cs.append(c)
    try:
        db.session.add_all(cs)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('vote.root'))
@vote.route('/vote/populate')
def populate(): 
    vis = []
    for i in range(5):
        vi = VoteInfo(
            title=f.bs(),
            subtitle=f.company_suffix(),
            description=f.credit_card_full(),
            admin="tzy15368@outlook.com"
            )
        vis.append(vi)
    try:
        db.session.add_all(vis)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return redirect(url_for('vote.root'))