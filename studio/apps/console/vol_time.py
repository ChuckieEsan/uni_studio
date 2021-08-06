from flask import flash, render_template, redirect, request, g, url_for, current_app, session
from studio.apps.console import console
from studio.models import db, VolTime_old, VolTime
import os
import time
import re
import pandas as pd
import codecs
import chardet


@console.route('/vol_time/update_by_array', methods=['POST'])
def update_by_array():
    dataSheet = request.get_json()
    for i in range(len(dataSheet)):
        dataArray = dataSheet[i]
        if len(dataArray) != 11:
            return("操作失败，数据异常")
        if re.match(r"^\d+$", dataArray[3]) is None:
            return("操作失败，数据异常")
        if re.match(r"^(\d{1,3}|\d{1,3}\.\d+)$", dataArray[4]) is None:
            return("操作失败，数据异常")
        if re.match(r"^\d{4}\/\d{1,2}\/\d{1,2}$", dataArray[8]) is None:
            return("操作失败，数据异常")

    old_rows = get_rows()
    try:
        for i in range(len(dataSheet)):
            dataArray = dataSheet[i]
            line_volTime = VolTime(
                id=0,
                name=dataArray[0],
                sex=dataArray[1],
                faculty=dataArray[2],
                stu_id=dataArray[3],
                duration=dataArray[4],
                activity_name=dataArray[5],
                activity_faculty=dataArray[6],
                team=dataArray[7],
                activity_date_str="",
                activity_DATE=dataArray[8],
                duty_person=dataArray[9],
                remark=dataArray[10])
            db.session.add(line_volTime)
            db.session.commit()
        current_app.logger.info("load data ok")
        new_rows = get_rows()
        return('操作成功，插入'+(str(new_rows-old_rows))+"条新数据")
    except Exception as e:
        current_app.logger.error(e)
        return("操作失败，原有"+str(old_rows)+"条，现有"+str(get_rows())+"条")


@console.route('/vol_time', methods=['POST'])
def do_vol_time_update():
    old_rows = get_rows()
    fname = request.values.get('fileIndex')
    coverall = request.values.get('coverall') != None
    files = [f for f in os.listdir(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id)))
             if os.path.isfile(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id), f))]
    if fname not in files:
        flash('无效的文件')
        return render_template("vol_time_update.html", count=old_rows)
    if fname[-4:] != '.csv':
        flash('文件格式错误')
        return render_template("vol_time_update.html", count=old_rows)
    fpath = os.path.join(
        current_app.config['FILESERVICE_UPLOAD_FOLDER'], str(g.user.id), fname)
    with open(fpath, 'rb') as f:
        data = f.read(512)
        code_type = chardet.detect(data)['encoding']
        if 'utf' not in code_type.lower():
            flash("文件编码({})错误，转换成csv UTF-8编码".format(code_type))
            return render_template("vol_time_update.html", count=old_rows)
    # new_file_path = os.path.join(os.getcwd(),"data",str(time.time())+".csv")
    # r = os.popen("iconv -f gbk -t utf8 {} -o {}".format(fpath,new_file_path))
    # r.read()
    # fpath = new_file_path
    df = pd.read_csv(fpath, nrows=1)
    columns = df.columns
    valid_columns = ['id', 'name', 'sex', 'faculty', 'stu_id', 'time', 'activity_name',
                     'activity_faculty', 'team', 'activity_time', 'duty_person']
    for c in columns:
        if c not in valid_columns:
            flash('csv头错误，参考样表核对文件格式')
            return render_template("vol_time_update.html", count=old_rows)
    if coverall:
        db.session.execute("truncate table vol_time")
        db.session.commit()
        current_app.logger.info("truncate ok")
    try:
        cursor = db.session.execute("load data local infile '"+fpath+"' ignore into table vol_time character set utf8mb4 fields \
            terminated by ',' optionally enclosed by '\"' escaped by '\"' lines terminated by '\\r\\n' ignore 1 lines;")
        db.session.commit()
        current_app.logger.info("load data ok")
        new_rows = get_rows()
        flash('操作成功，插入'+(str(new_rows-old_rows)
                         if not coverall else str(new_rows))+"条新数据")
    except Exception as e:
        current_app.logger.error(e)
        flash("操作失败，原有"+str(old_rows)+"条，现有"+str(get_rows())+"条")
    return render_template("vol_time_update.html", count=get_rows())


def get_rows():
    cursor = db.session.execute("select count(*) from vol_time")
    res = cursor.fetchall()
    count = res[0][0]
    return count


@console.route('/vol_time', methods=['GET'])
def show_vol_time_update():
    return render_template("vol_time_update.html", title="志愿时长查询增量更新", count=get_rows())
