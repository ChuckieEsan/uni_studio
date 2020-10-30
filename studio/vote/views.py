from studio.vote import vote
from studio.models import VoteInfo,VoteCandidates,VoteVotes,db
from flask import url_for,redirect,render_template,request
from faker import Faker
import json
f=Faker(locale='zh_CN')
@vote.route("/")
def root():
    voteinfo_all = VoteInfo.query.all()
    return render_template(
        'vote_index.html',
        info_list=voteinfo_all
        )

@vote.route('/<int:vote_id>',methods=["GET"])
def vote_page(vote_id):
    candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id==vote_id).all()
    return render_template(
        'vote_vote_page.html',
        candidate_all = candidate_all
    )

@vote.route('/<int:vote_id>',methods=["POST"])
def vote_handler(vote_id):
    voted = VoteVotes.query.filter(VoteVotes.ip==request.remote_addr).filter(VoteVotes.vote_id==vote_id).first()
    if voted:
        pass
        #return "volted!"
    vote_list = request.get_json()
    #votes_list = json.loads(votes)
    print(vote_list)
    vs=[]
    id_list = []
    for v in vote_list:
        if v.get('candidate') == None:
            continue
        print(v)
        _v = VoteVotes(
            ip = request.remote_addr,
            candidate = int(v['candidate']),
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
    return redirect(url_for('vote.root')+str(vote_id))

@vote.route('/populate/<vote_id>')
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
@vote.route('/populate')
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