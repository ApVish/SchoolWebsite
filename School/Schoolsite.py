from flask import Flask, render_template, request, redirect, url_for, flash
import os
import xlrd
import csv
import MySQLdb


app = Flask(__name__)


conn = MySQLdb.connect(host="localhost", port=3306, user="root", password="root", db="school")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/homepage')
@app.route('/')
def index(user=None):
    return render_template("homepage.html")


@app.route('/home')
def home():
    return render_template("Home.html")


@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        if uname=='admin' and pwd=='12345':
            return render_template("adminpage.html")
    return render_template("admin.html")


@app.route('/adminpage')
def adminpage():
    return render_template("adminpage.html")


@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        email = str(request.form['email'])
        pwd = str(request.form['pwd'])
        cursor = conn.cursor()
        cursor.execute("select email,pwd from teachers where email=%s",(email,))
        data=cursor.fetchone()
        if pwd==data[1]:
            return render_template("Home.html")
    return render_template("login.html")


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        sec = request.form['sec']
        sem = request.form['sem']
        semsec = sem+sec
        target = os.path.join(APP_ROOT, 'stufiles/')
        if not os.path.isdir(target):
            os.mkdir(target)
        for file in request.files.getlist("students"):
            filename = file.filename
            destination = "/".join([target, filename])
            file.save(destination)
            wb = xlrd.open_workbook(destination)
            sh = wb.sheet_by_index(0)
            csv_file = open('students.csv', 'w')
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for rownum in range(sh.nrows):
                wr.writerow(sh.row_values(rownum))
            csv_file.close()
            uploadToDB(semsec)
        return redirect(url_for("adminpage"))
    return render_template("upload.html")


@app.route('/teacherdetails', methods=["GET", "POST"])
def teacherdetails():
    if request.method == 'POST':
        email = str(request.form['email'])
        name = str(request.form['fname'])
        pwd = str(request.form['pwd'])
        cursor = conn.cursor()

        cursor.execute("INSERT INTO teachers VALUES (%s,%s,%s)",(email, name, pwd,))
        conn.commit()
        return redirect(url_for("adminpage"))
    return render_template("teachdetails.html")


@app.route('/attregister',methods=["GET", "POST"])
def attregister():
    if request.method == 'POST':
        sec = request.form['sec']
        sem = request.form['sem']
        semsec=sem+sec

        query = "SELECT rno,sname from "+semsec+" order by rno"

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return render_template("attendance.html", data=data)
    return render_template("attendancesec.html")


@app.route('/markattendance',methods=["GET", "POST"])
def markattendance():
    if request.method == 'POST':
        rnos = request.form.getlist('rollnum')
        return redirect(url_for("home"))


@app.route('/marks',methods=["GET", "POST"])
def marks():
    if request.method == 'POST':
        sem = request.form['sem']
        sec = request.form['sec']
        semsec = sem+sec
        query = "SELECT rno,sname,sub1,sub2,sub3,sub4,sub5,sub6 from "+ semsec +" order by rno"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return render_template("marks.html", data=data)

    return render_template("markssec.html")


def uploadToDB(semsec):
    f = open(r"students.csv","r")
    fstring = f.read()
    dbname=semsec
    fstr=""
    for i in fstring:
        if i!='\"':
            fstr = fstr+i
    print(fstr)
    flist = []
    for line in fstr.split('\n\n'):
        flist.append(line.split(','))
    print(flist)
    db = MySQLdb.connect("localhost","root","root","school")
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS "+ dbname)
    SNAME = flist[0][0]
    PNAME = flist[0][1]
    ADM_ID = flist[0][2]
    RNO = flist[0][3]
    PHNO = flist[0][4]
    SUB1 = flist[0][5]
    SUB2 = flist[0][6]
    SUB3 = flist[0][7]
    SUB4 = flist[0][8]
    SUB5 = flist[0][9]
    SUB6 = flist[0][10]
    querycreate= """CREATE TABLE """+ dbname + """(
                    {} VARCHAR(100) NOT NULL,
                    {} VARCHAR(100) NOT NULL,
                    {} decimal(10,0) NOT NULL,
                    {} decimal(10,0) NOT NULL,
                    {} decimal(10,0) NOT NULL,
                    {} decimal(3,0),
                    {} decimal(3,0),
                    {} decimal(3,0),
                    {} decimal(3,0),
                    {} decimal(3,0),
                    {} decimal(3,0)
                    )""".format(SNAME,PNAME,ADM_ID,RNO,PHNO,SUB1,SUB2,SUB3,SUB4,SUB5,SUB6)
    cursor.execute(querycreate)
    del flist[0]
    rows = ""
    for i in range(len(flist)-1):
        rows += "('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(flist[i][0], flist[i][1], flist[i][2], flist[i][3], flist[i][4], flist[i][5], flist[i][6], flist[i][7], flist[i][8], flist[i][9], flist[i][10])
        if i != len(flist) - 2:
            rows += ','
    print(rows)
    queryinsert = "INSERT INTO "+ dbname+" VALUES "+ rows
    cursor.execute(queryinsert)
    db.commit()
    db.close()


if __name__ == "__main__":
    app.run(debug=True)
