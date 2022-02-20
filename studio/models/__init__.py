from .base import db, EditHistory, MixinBase
from .chat import ChatBody, ChatHead
from .enroll import EnrollCandidates, EnrollForms
from .issues import IssueIssues, IssueTypes
from .notification import NotificationsGlobal
from .points import Points
from .postcard import PostcardCards, PostcardRoles, PostcardTemplates, PostcardUsers
from .route import RouteInterceptors
from .user import UserUsers, UserRoles
from .voltime import VoltimeOld, Voltime, VoltimeDupname
from .vote import VoteInfo, VoteVotes, VoteCandidates

from sqlalchemy import event, inspect
from sqlalchemy.orm import attributes, make_transient, Session, with_loader_criteria
from flask import g


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    print('before_flush')
    print(session.dirty)
    print(session.new)
    print(session.deleted)
    for instance in session.dirty:
        # 导致dirty的原因不止是“修改”
        if not session.is_modified(instance):
            continue
        if not attributes.instance_state(instance).has_identity:
            continue
        # 此处可以修改属性值，同样会使has_changes()为True
        # instance.team = 'before_flush'
        for attr in inspect(instance).attrs:
            if attr.history.has_changes():
                edit = EditHistory(type="modified",
                                   table_name=instance.__tablename__,
                                   row_id=instance.id,
                                   attr_name=attr.key,
                                   details=str(attr.history),
                                   edit_by=g.user.id if g.user is not None else 0)
                session.add(edit)

    for instance in session.deleted:
        make_transient(instance)  # 取消当前操作
        target = session.query(instance.__class__).filter_by(id=instance.id).one()  # 重新拿到当前记录
        target.deleted = True  # 添加删除标记
        session.add(target)  # 提交新操作

        edit = EditHistory(type="deleted", table_name=instance.__tablename__, row_id=instance.id, edit_by=g.user.id)
        session.add(edit)


@event.listens_for(Session, "do_orm_execute")
def do_orm_execute(orm_execute_state):
    print('\ndo_orm_execute')
    print('is_delete:', orm_execute_state.is_delete)
    print('is_insert:', orm_execute_state.is_insert)
    print('is_select:', orm_execute_state.is_select)
    print('is_update:', orm_execute_state.is_update)

    if (orm_execute_state.is_select and not orm_execute_state.is_column_load
            and not orm_execute_state.is_relationship_load):
        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(MixinBase,
                                 lambda cls: cls.deleted == False,
                                 include_aliases=True,
                                 propagate_to_loaders=False))
        # orm_execute_state.statement = orm_execute_state.statement.filter_by(deleted=False)

    print(orm_execute_state.statement)
