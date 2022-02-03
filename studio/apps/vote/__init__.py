from flask import Blueprint, current_app
from studio.models import VoteInfo, VoteCandidates, VoteVotes, db
vote = Blueprint("vote", __name__, template_folder='templates', static_folder='static')
#static folder and template folder are set here to avoid ambiguity
from studio.utils.cache import cache


@cache.memoize(20)
def get_vote_info(vote_id: int):
    return VoteInfo.query.filter(VoteInfo.id == vote_id).first_or_404()


@cache.memoize(20)
def get_candidate_all_info(vote_id: int):
    candidates_all = VoteCandidates.query.filter(VoteCandidates.vote_id == vote_id).all()
    for c in candidates_all:
        c.description = c.description.replace('<br>', '\n')
        c.description = c.description.replace('\r', '').replace('\n', '<br/>').replace('<br>', '<br/>').strip()
    return candidates_all


@cache.memoize(20)
def get_candidate_info(c_id: int):
    return VoteCandidates.query.filter(VoteCandidates.id == c_id).first()


from studio.apps.vote import views
