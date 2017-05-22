from flask import Flask,request
from flaskext.mysql import MySQL
from datetime import date,timedelta
import datetime
import json

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'wakasann'
app.config['MYSQL_DATABASE_DB'] = 'masturbation'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#define now()
now = datetime.datetime.now()

def weekBoundaries(year,week):
    startOfYear = date(year, 1, 1)
    week0 = startOfYear - timedelta(days=startOfYear.isoweekday())
    sun = week0 + timedelta(weeks=week)
    sat = sun + timedelta(days=6)
    return sun, sat



@app.route('/record/<int:user_id>')
def home(user_id):

    user_id = str(user_id)

    if user_id != '64':
        result = {'error_code':1,'error_message':'user not found','result':''}
        return json.dumps(result)

    today = now.strftime('%Y-%m-%d') # get current date

    # get current week,start date and end date
    year = now.strftime('%Y')
    week = now.strftime('%U')
    week_dates = weekBoundaries(int(year),int(week))
    week_start_date = str(week_dates[0])
    week_end_date = str(week_dates[1])

    # get current month first day date,last day date
    current_today = datetime.date.today()
    cur_date_first = datetime.datetime(current_today.year, current_today.month, 1)
    cur_date_last = datetime.datetime(current_today.year, current_today.month + 1,
                                      1) - datetime.timedelta(1)
    cur_date_first = str(cur_date_first.strftime('%Y-%m-%d'))
    cur_date_last = str(cur_date_last.strftime('%Y-%m-%d'))

    cursor = mysql.connect().cursor()
    # get today count
    today_args = (user_id,today)
    today_sql = "SELECT count(*) as count FROM mainlog where user_id=%s" \
                + " AND logdate= %s AND deleted='0';"
    cursor.execute(today_sql,today_args)
    today_count = cursor.fetchone()
    # get week count
    week_args = (user_id,week_start_date,week_end_date)
    week_sql = "SELECT count(*) as count FROM mainlog where user_id=%s"\
                + " AND logdate between %s " \
                + " AND %s AND deleted='0';"
    cursor.execute(week_sql,week_args)
    week_count = cursor.fetchone()
    # get month count
    month_args = (user_id,cur_date_first,cur_date_last)
    month_sql = "SELECT count(*) as count FROM mainlog where user_id=%s" \
               + " AND logdate between %s " \
               + " AND %s; AND deleted='0'"
    cursor.execute(month_sql,month_args)
    month_count = cursor.fetchone()

    cursor.close()
    mysql.connect().close()

    return_data = {}
    return_data['week'] = [week_start_date,week_end_date,str(week_count[0])]
    return_data['month'] = [cur_date_first, cur_date_last, str(month_count[0])]
    return_data['today'] = str(today_count[0])

    result = {'error_code':0,'error_message':'success','result':return_data}

    json_str = json.dumps(result)
    return json_str

@app.route('/record/add',methods=['GET','POST'])
def record_add():
    if request.method == 'POST':
        #define the result data
        result = {'error_code': 0, 'error_message': 'success', 'result': ''}
        #get post data
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        user_id = request.form['user_id']
        logdate = request.form['logdate']

        if user_id != '64':
            result = {'error_code': 1, 'error_message': 'user not found', 'result': ''}
            return json.dumps(result)

        #validate the data
        if start_time is None:
            result['error_code'] = 1
            result['error_message'] = 'start time should be a datetime'
            return json.dumps(result)
        elif end_time is None:
            result['error_code'] = 1
            result['error_message'] = 'end time should be a datetime'
            return json.dumps(result)
        elif user_id is None:
            result['error_code'] = 1
            result['error_message'] = 'user id should be a numer'
            return json.dumps(result)

        logdate = logdate if logdate is None else now.strftime('%Y-%m-%d')

        cursor = mysql.connect().cursor()
        try:
            args = (user_id,logdate,start_time,end_time,now.strftime('%Y-%m-%d %H:%M:%S'))
            insert_sql = "INSERT INTO mainlog (user_id,logdate,start_time,end_time,created_at) Value(" \
                         "%s,%s,%s,%s,%s);"
            cursor.execute(insert_sql,args)
            mysql.connect().commit()
        except cursor.IntegrityError:
            result['error_code'] = 1
            result['error_message'] = 'add fail,please try again'
            return json.dumps(result)

        cursor.close()
        mysql.connect().close()
        return json.dumps(result);
    else:
        return 'your request method should POST'



@app.route('/record/edit',methods=['GET','POST'])
def record_edit():
    if request.method == 'POST':
        #define the result data
        result = {'error_code': 0, 'error_message': 'success', 'result': ''}
        #get post data
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        user_id = request.form['user_id']
        logdate = request.form['logdate']
        id = request.form['id']

        if user_id != '64':
            result = {'error_code': 1, 'error_message': 'user not found', 'result': ''}
            return json.dumps(result)

        #validate the data
        if start_time is None:
            result['error_code'] = 1
            result['error_message'] = 'start time should be a datetime'
            return json.dumps(result)
        elif end_time is None:
            result['error_code'] = 1
            result['error_message'] = 'end time should be a datetime'
            return json.dumps(result)
        elif user_id is None:
            result['error_code'] = 1
            result['error_message'] = 'user id should be a numer'
            return json.dumps(result)

        logdate = logdate if logdate is None else now.strftime('%Y-%m-%d')

        cursor = mysql.connect().cursor()
        try:
            args = (logdate,start_time,end_time,now.strftime('%Y-%m-%d %H:%M:%S'),user_id,id)
            update_sql = "UPDATE mainlog set logdate=%s,start_time=%s,end_time=%s,update_at=%s WHERE" \
                         + " user_id=%s AND id=%s;"
            cursor.execute(update_sql,args)
            mysql.connect().commit()
        except cursor.IntegrityError:
            result['error_code'] = 1
            result['error_message'] = 'update fail,please try again'
            return json.dumps(result)

        cursor.close()
        mysql.connect().close()
        return json.dumps(result);
    else:
        return 'your request method should POST'

@app.route('/record/delete',methods=['GET','POST'])
def record_delete():
    if request.method == 'POST':
        #define the result data
        result = {'error_code': 0, 'error_message': 'success', 'result': ''}
        #get post data
        user_id = request.form['user_id']
        id = request.form['id']

        if user_id != '64':
            result = {'error_code': 1, 'error_message': 'user not found', 'result': ''}
            return json.dumps(result)

        #validate the data
        if user_id is None:
            result['error_code'] = 1
            result['error_message'] = 'user id should be a numer'
            return json.dumps(result)
        elif id is None:
            result['error_code'] = 1
            result['error_message'] = 'id should be a numer'
            return json.dumps(result)

        cursor = mysql.connect().cursor()
        try:
            args = (user_id,id)
            update_sql = "UPDATE `mainlog` set `deleted`='0' where `user_id`=%s AND `id`=%s"
            cursor.execute(update_sql,args)
            mysql.connect().commit()
        except cursor.IntegrityError:
            result['error_code'] = 1
            result['error_message'] = 'delete fail,please try again'
            return json.dumps(result)

        cursor.close()
        mysql.connect().close()
        return json.dumps(result);
    else:
        return 'your request method should POST'


@app.errorhandler(404)
def page_not_found(error):
    result = {'error_message':'404 Not Found'}
    return json.dumps(result)

@app.errorhandler(405)
def page_not_found(error):
    result = {'error_message':'Method Not Allowed'}
    return json.dumps(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True);