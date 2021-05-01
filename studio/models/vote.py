from .base import db
from .mixins import TimestampMixin


class VoteVotes(TimestampMixin, db.Model):
    __tablename__ = "vote_voters"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), nullable=False)
    candidate = db.Column(db.Integer, nullable=False)  # candidates id
    vote_id = db.Column(db.Integer, nullable=False)  # vote info id

    def __init__(self, *args, **kwargs):
        super(VoteVotes, self).__init__(**kwargs)

    def __str__(self):
        return "<Vote NO {}>".format(self.id)


class VoteCandidates(TimestampMixin, db.Model):
    __tablename__ = "vote_candidates"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    action_at = db.Column(db.Text, nullable=True)
    votes = db.Column(db.Integer, default=0, nullable=False)
    vote_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.Text, nullable=True)

    def __init__(self, *args, **kwargs):
        super(VoteCandidates, self).__init__(**kwargs)

    def __str__(self):
        return str(self.todict())#"<Candidate NO {}>".format(self.id)
    def todict(self):
        return self.__dict__


class VoteInfo(TimestampMixin, db.Model):
    __tablename__ = "vote_info"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text, default='', nullable=True)
    description = db.Column(db.Text, default='', nullable=True)
    image = db.Column(db.Text, nullable=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    start_at = db.Column(db.DateTime(
        True), default=db.func.now(), nullable=True)
    end_at = db.Column(db.DateTime(True), default=db.func.now(), nullable=True)
    vote_min = db.Column(db.Integer, default=0, nullable=False)
    vote_max = db.Column(db.Integer, default=999, nullable=False)
    admin = db.Column(db.Text, nullable=False)
    shuffle = db.Column(db.Boolean, default=False, nullable=False)
    is_poll = db.Column(db.Boolean, default=False, nullable=False)
    show_stats = db.Column(db.Boolean,default=False)
    show_raw_vote_on_expire = db.Column(db.Boolean,default=False)
    title_label = db.Column(db.String(255))#每一个选项的大标题的label
    subtitle_label = db.Column(db.Text)#每一个选项的副标题的label
    def __init__(self, *args, **kwargs):
        super(VoteInfo, self).__init__(**kwargs)

    def __str__(self):
        return "<VoteInfo NO {}>".format(self.id)
