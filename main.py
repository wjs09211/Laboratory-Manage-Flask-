# encoding:utf8
import flask
import flask_login
import sqlite3
import datetime
from werkzeug import security
import os
from werkzeug import secure_filename
from flask import jsonify

from checkInput import *
UPLOAD_FOLDER = 'upload/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'rar', 'zip', 'ppt', 'pptx'}

app = flask.Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

con = sqlite3.connect("testTable.sqlite")


class User(flask_login.UserMixin):
    def __init__(self, user_id, account):
        self.id = user_id
        self.account = account


@login_manager.user_loader
def user_loader(user_id):
    cur = con.cursor()
    cur.execute("select id, account from User WHERE id=?", user_id)
    ret = cur.fetchone()
    if ret is None:
        return
    user = User(user_id, ret[1])
    return user


@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('user_id')
    if user_id is None:
        return
    cur = con.cursor()
    cur.execute("select id, account from User WHERE id=?", user_id)
    ret = cur.fetchone()
    user = User(user_id, ret[1])
    return user


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html', Error=False)
    elif flask.request.method == 'POST':
        flask_login.logout_user()
        account = flask.request.form['account']
        if not check_acc_pwd(account):
            return flask.render_template('login.html', acc_err=True)
        password = flask.request.form['pw']
        if not check_acc_pwd(password):
            return flask.render_template('login.html', pwd_err=True)
        cur = con.cursor()
        cur.execute("select id, account, password from User WHERE account=? AND password=?", (account, password))
        ret = cur.fetchone()
        if ret is None:
            return flask.render_template('login.html', Error=True)
        elif ret[1] == account and ret[2] == password:
            user = User(ret[0], ret[1])
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('index'))
        return 'Bad login'


@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template('register.html')
    elif flask.request.method == 'POST':
        account = flask.request.form['account']
        if not check_acc_pwd(account):
            return flask.render_template('register.html', acc_err=True)
        password = flask.request.form['pw']
        if not check_acc_pwd(password):
            return flask.render_template('register.html', pwd_err=True)
        name = flask.request.form['name']
        if not check_acc_pwd(name, 1):
            return flask.render_template('register.html', name_err=True)
        email = flask.request.form['email']
        if not check_email(email):
            return flask.render_template('register.html', email_err=True)

        cur = con.cursor()
        cur.execute("select id, account from User WHERE account=?", (account,))
        ret = cur.fetchone()
        if ret is not None:
            return flask.render_template('register.html', Error=True)

        cur.execute("INSERT INTO User (account, password, name, email) VALUES (?, ?, ?, ?)",
                    (account, password, name, email))
        con.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', Error=True)


@app.route('/index.html')
def index():
    # user = flask_login.current_user._get_current_object()
    # print "protected", flask_login.current_user._get_current_object()
    # return 'Logged in as: ' + flask_login.current_user.id
    return flask.render_template('index.html', index=True)


@app.route('/balance.html', methods=['GET', 'POST'])
@flask_login.login_required
def balance():
    if flask.request.method == 'GET':
        income_err = False
        outlay_err = False
        input_err = False
        try:
            income_err = flask.request.args['income_err']
        except:
            pass
        try:
            outlay_err = flask.request.args['outlay_err']
        except:
            pass
        try:
            input_err = flask.request.args['input_err']
        except:
            pass
        money = 10000
        cur = con.cursor()
        cur.execute("SELECT name, content, income, outlay, time FROM LabBalance ORDER BY id DESC")
        ret = cur.fetchall()
        for item in ret:
            money += item[2]
            money -= item[3]
        return flask.render_template('balance.html', money=money, ret=ret, balance=True,
                                     income_err=income_err, outlay_err=outlay_err, input_err=input_err)
    elif flask.request.method == 'POST':
        name = flask.request.form['name']
        content = flask.request.form['content']
        income = flask.request.form['income']
        if not check_integer(income):
            return flask.redirect(flask.url_for('balance', income_err=True))
        elif int(income) < 0:
            return flask.redirect(flask.url_for('balance', income_err=True))
        outlay = flask.request.form['outlay']
        if not check_integer(outlay):
            return flask.redirect(flask.url_for('balance', outlay_err=True))
        elif int(outlay) < 0:
            return flask.redirect(flask.url_for('balance', outlay_err=True))
        if int(outlay) != 0 and int(income) !=0:
            return flask.redirect(flask.url_for('balance', input_err=True))
        cur = con.cursor()
        cur.execute("INSERT INTO LabBalance (name, content, income, outlay) VALUES (?, ?, ?, ?)",
                    (name, content, income, outlay))
        con.commit()
        return flask.redirect(flask.url_for('balance'))


@app.route('/equip.html', methods=['GET', 'POST'])
@flask_login.login_required
def equip():
    if flask.request.method == 'GET':
        cur = con.cursor()
        cur.execute("SELECT name, state, buy_time, end_time, keeper FROM LabEquip ORDER BY id DESC")
        ret = cur.fetchall()

        days_list = []
        for item in ret:
            end_time = str(item[3]).split("-")
            date_end = datetime.date(int(end_time[0]), int(end_time[1]), int(end_time[2]))
            d = datetime.datetime.now()
            date_now = datetime.date(getattr(d, "year"), getattr(d, "month"), getattr(d, "day"))
            days = date_end - date_now
            days_list.append(days.days)

        return flask.render_template('equip.html', equip=True, ret=ret, days_list=days_list)
    elif flask.request.method == 'POST':
        name = flask.request.form['name']
        state = flask.request.form['state']
        buy_time = flask.request.form['buy_time']
        end_time = flask.request.form['end_time']
        keeper = flask.request.form['keeper']

        cur = con.cursor()
        cur.execute("INSERT INTO LabEquip (name, state, buy_time, end_time, keeper) VALUES (?, ?, ?, ?, ?)",
                    (name, state, buy_time, end_time, keeper))
        con.commit()
        return flask.redirect(flask.url_for('equip'))


@app.route('/meetingSchedule.html', methods=['GET', 'POST'])
@flask_login.login_required
def meeting_schedule():
    if flask.request.method == 'POST':
        name = flask.request.form['name']
        content = flask.request.form['content']
        location = flask.request.form['location']
        start_time = flask.request.form['start_time']
        end_time = flask.request.form['end_time']
        participants = flask.request.form['participants']
        keeper = flask.request.form['keeper']
        cur = con.cursor()
        cur.execute(
            "INSERT INTO MeetingSchedule (name, content, location, start_time, end_time, participants, keeper) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, content, location, start_time, end_time, participants, keeper))
        con.commit()
        return flask.redirect(flask.url_for('meeting_schedule'))

    elif flask.request.method == 'GET':
        cur = con.cursor()
        cur.execute("SELECT id, name, start_time, end_time "
                    "FROM MeetingSchedule")
        ret = cur.fetchall()
        data = []
        for r in ret:
            dis = {'id': r[0],
                   'title': r[1],
                   'start': r[2],
                   'end': r[3]
                   }
            data.append(dis)
        return flask.render_template("meetingSchedule.html", meetingSchedule=True, data=data,
                                     now=datetime.datetime.now().strftime("%Y-%m-%d"))


@app.route('/scheduleItem.html', methods=['GET'])
@flask_login.login_required
def scheduleItem():
    schedule_id = flask.request.args.get('id')
    cur = con.cursor()
    cur.execute("SELECT name, content, location, start_time, end_time, participants, keeper "
                "FROM MeetingSchedule WHERE id=?", schedule_id)
    ret = cur.fetchone()
    if ret is not None:
        return flask.render_template("scheduleItem.html", ret=ret)
    return "bad request"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/paper.html', methods=['GET', 'POST'])
@flask_login.login_required
def paper():
    if flask.request.method == 'POST':
        upload_file = flask.request.files['upload_file']
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            path_origin = path
            i = 1
            while os.path.exists(path):
                if i == 1:
                    temp_name, extension = path.rsplit(".")[0:2]
                else:
                    temp_name, extension = path.rsplit(".")[0:2]
                    temp_name = path_origin
                print temp_name, extension
                temp_name += "(" + str(i) + ")"
                path = temp_name + "." + extension
                i += 1
            upload_file.save(path)

            user = flask_login.current_user._get_current_object()
            cur = con.cursor()
            cur.execute("INSERT INTO Paper (name, path, keeper) VALUES (?, ?, ?)",
                        (filename, path, user.account))
            con.commit()
            return flask.redirect(flask.url_for('paper', filename=filename))
        else:
            return flask.redirect(flask.url_for('paper'))
    else:
        cur = con.cursor()
        cur.execute("SELECT name, path, time, keeper FROM Paper ORDER BY id DESC")
        ret = cur.fetchall()
        return flask.render_template('paper.html', paper=True, ret=ret)


@app.route("/upload/<file_name>")
@flask_login.login_required
def get_file(file_name):
    print file_name
    return flask.send_file("upload/" + file_name, as_attachment=True)


# @app.route('/child.html')
# def child():
#     return flask.render_template('child.html')


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return flask.render_template('login.html', show=True)


@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))


@app.route('/')
def hello_world():
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    # app.run()
