from flask import Blueprint, jsonify, request
from studio.models import db, VoltimeOld, Voltime, VoltimeDupname

voltime = Blueprint('voltime', __name__, url_prefix='/voltime')


@voltime.route('/', methods=['POST'])
def r_vol_time_search():
    req = request.get_json()
    respDict = {'name': req['name'], 'lstVoltimes': [], 'totalDuration': 0}

    results = db.session.query(VoltimeOld.id)\
        .filter(VoltimeOld.stu_id == req['stu_id'], VoltimeOld.name == req['name']).all()
    setIdsOld = set([result[0] for result in results])

    resVoltimes = db.session.query(Voltime)\
        .filter(Voltime.stu_id == req['stu_id'], Voltime.name == req['name'])\
        .order_by(Voltime.activity_DATE.desc()).all()
    for rowVoltime in resVoltimes:
        rowVoltime = rowVoltime.__dict__
        rowVoltime.pop('_sa_instance_state')
        rowVoltime['activity_DATE'] = rowVoltime['activity_DATE'].strftime('%Y-%m-%d')\
            if rowVoltime['activity_DATE'].year > 2005 else rowVoltime['activity_date_str']
        rowVoltime['queryNewly'] = False if rowVoltime['id'] in setIdsOld or rowVoltime['id'] > 100000 else True
        respDict['lstVoltimes'].append(rowVoltime)
        respDict['totalDuration'] += float(rowVoltime['duration'])

    setIdsNow = set([voltime['id'] for voltime in respDict['lstVoltimes']])
    respDict['isErrQueryLost'] = True if len(setIdsOld.difference(setIdsNow)) > 0 else False

    respDict['numSameID'] = db.session.query(Voltime.name)\
        .filter(Voltime.stu_id == req['stu_id']).group_by(Voltime.name).count()
    respDict['numSameName'] = db.session.query(Voltime.stu_id)\
        .filter(Voltime.name == req['name']).group_by(Voltime.stu_id).count()

    resDupName = db.session.query(VoltimeDupname).filter(VoltimeDupname.name == req['name']).first()
    respDict['numDupName'] = 1 if resDupName is None else resDupName.dupNum
    return jsonify(respDict)


@voltime.route('/last-date')
def vol_time_home():
    lastDate = db.session.query(Voltime.activity_DATE)\
        .order_by(Voltime.activity_DATE.desc()).limit(1).scalar()
    lastDate = lastDate.strftime('%Y-%m-%d')
    return jsonify({'lastDate': lastDate})
