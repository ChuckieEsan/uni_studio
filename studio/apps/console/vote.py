from flask.helpers import send_file
from flask import make_response
from .init import console as vote
from studio.utils.time_helper import timestamp_to_datetime
from studio.utils.hash_helper import md5
from studio.apps.vote import get_candidate_all_info, get_vote_info
from studio.models import VoteInfo, VoteCandidates, VoteVotes, db
from flask import url_for, redirect, abort, render_template, request, Markup, g, current_app
from faker import Faker
import pandas as pd
import time
import os
from io import BytesIO
from slugify import slugify
f = Faker(locale='zh_CN')


@vote.route('/vote', methods=["GET"])  # 投票管理大厅，能看所有投票
def admin_votes_show():
    voteinfo_all = VoteInfo.query.filter().all()
    return render_template('vote_admin_index.html', info_list=voteinfo_all, title="Vote Admin")


@vote.route('/vote', methods=["POST"])  # 新建投票接口
def admin_votes_add():
    #new_vote = request.get_json()
    new_vote = request.form
    v = VoteInfo(title=new_vote.get("title"),
                 subtitle=new_vote.get("subtitle"),
                 description=new_vote.get("description"),
                 image=new_vote.get("image"),
                 start_at=timestamp_to_datetime(new_vote.get("start_at")),
                 end_at=timestamp_to_datetime(new_vote.get("end_at")),
                 vote_min=new_vote.get("vote_min"),
                 vote_max=new_vote.get("vote_max"),
                 title_label=new_vote.get('title_label'),
                 subtitle_label=new_vote.get('subtitle_label'),
                 admin=g.user.id)
    db.session.add(v)
    db.session.commit()
    return redirect(url_for('console.admin_votes_show'))


@vote.route('/vote/<int:vote_id>', methods=["GET"])
def admin_vote_page(vote_id):
    candidate_all = VoteCandidates.query.filter(VoteCandidates.vote_id == vote_id).all()
    vote_info = VoteInfo.query.filter(VoteInfo.id == vote_id).first_or_404()
    for c in candidate_all:
        c.description = Markup(c.description)
    return render_template('vote_admin_vote_page.html',
                           candidate_all=candidate_all,
                           vote_info=vote_info,
                           title=vote_info.title)


@vote.route('/vote/stats/<int:vote_id>')
def show_vote_stats(vote_id):
    vote_info = get_vote_info(vote_id=vote_id)
    candidates_all = sorted(get_candidate_all_info(vote_id=vote_id), key=lambda x: x.votes, reverse=True)
    return render_template('vote_stats.html', vote_info=vote_info, candidates_all=candidates_all)


@vote.route('/vote/export/<int:vote_id>')
def vote_export(vote_id):
    vote_info = get_vote_info(vote_id=vote_id)
    candidates_all = sorted(get_candidate_all_info(vote_id=vote_id), key=lambda x: x.votes, reverse=True)
    result_list = []
    for c in candidates_all:
        result_list.append(
            {'id': c.id,
             str(vote_info.title_label): c.title,
             str(vote_info.subtitle_label): c.subtitle, '票数': c.votes})
    df = pd.DataFrame(result_list, columns=['id', str(vote_info.title_label), str(vote_info.subtitle_label), '票数'])

    out = BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    df.to_excel(excel_writer=writer, index=False)
    writer.save()
    writer.close()
    resp = make_response(out.getvalue())
    resp.headers["Content-Disposition"] = "attachment; filename={}-{}.xlsx"\
        .format(slugify(vote_info.title), str(time.time()))
    resp.headers["Content-Type"] = "text/csv"
    return resp


@vote.route('/vote/<int:vote_id>/candidates', methods=["POST"])
def candidate_add(vote_id):
    new_candidate = request.form
    _des = new_candidate.get('description').strip()  # .replace('\n','<br>')
    c = VoteCandidates(
        title=new_candidate.get("title"),  # 姓名
        subtitle=new_candidate.get("subtitle"),  # 所在社区
        description=_des,  # new_candidate.get("description"),#周记
        vote_id=vote_id,
        action_at=new_candidate.get('action_at'),  # 时间
    )
    db.session.add(c)
    db.session.commit()
    return redirect(url_for('console.admin_vote_page', vote_id=vote_id))


@vote.route('/vote/<int:vote_id>/batchimport', methods=['POST'])
def do_vote_batch_import(vote_id):
    fname = request.values.get('fileIndex')
    coverall = request.values.get('coverall') != None
    files = [
        f for f in os.listdir(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id)))
        if os.path.isfile(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id), f))
    ]
    if fname not in files:
        abort(400)
    fpath = os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id), fname)
    df = pd.read_excel(fpath, engine='openpyxl', header=None)
    candidates = []
    for i in range(1, df.shape[0]):
        row = df.iloc[i]
        if row.isna().values.any():
            continue
        c = VoteCandidates(
            title=row[0],  # if row[0] != pd.Nan,
            subtitle=row[1],
            description=row[2],
            action_at=row[3],
            vote_id=vote_id)
        candidates.append(c)
    if coverall:
        old_candidates = VoteCandidates.query.filter(VoteCandidates.vote_id == vote_id).all()
        for o in old_candidates:
            db.session.delete(o)
    db.session.add_all(candidates)
    db.session.commit()
    return redirect(url_for('console.admin_vote_page', vote_id=vote_id))


@vote.route('/vote/<int:vote_id>/candidates/drop/<int:candidate_id>', methods=["GET"])
@vote.route('/vote/candidates/<candidate_id>', methods=["DELETE"])
def candidate_del(vote_id, candidate_id):
    VoteCandidates.query.filter(VoteCandidates.id == candidate_id).delete()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('console.admin_vote_page', vote_id=vote_id))


@vote.route('/vote/drop/<vote_id>', methods=["GET"])
@vote.route('/vote/<vote_id>', methods=["DELETE"])
def votes_del(vote_id):
    VoteInfo.query.filter(VoteInfo.id == vote_id).delete()
    # delete candidates and corresponding vote tickets?
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('console.admin_votes_show'))
