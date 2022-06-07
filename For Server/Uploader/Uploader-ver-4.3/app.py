from http import client
import json
from tabnanny import check
from turtle import speed
from flask import Flask, render_template, request, jsonify,redirect, url_for, flash
from flask_mysqldb import MySQL,MySQLdb
#from sqlalchemy import true #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from werkzeug.utils import secure_filename
import os
from datetime import datetime


app = Flask(__name__)

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gd'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

userType='visitor'
allowed_extensions = []#["gif", "png", "jpg", "jpeg", "bmp", "zip", "rar","exe","ova"]
allowed_size = []#[20971522097152, 22097152097152, 20971520971522, 20920971527152, 20920971527152, 20209715297152, 20920971527152,20920971527152,20920971527152]
allowed_speedUp, allowedDown = [],[]

adsTable=[]


@app.route('/')
def Run():
    changeUserAuth()
    
    return redirect(url_for('Main'))
    #allowed_extensions, allowed_size, allowed_speedUp, allowedDown = changeUserAuth()
    #return render_template('uploader/uploadfile.html')
    #return render_template("index.html")
    #return render_template("user/admin_users.html")

@app.route('/Main')
def Main():
    changeUserAuth(userType)
    #changeUpPath()
    getAds()
    return render_template('uploader/main.html',exts=json.dumps(allowed_extensions),sizes=json.dumps(allowed_size))
    #jsonify({'htmlresponse': render_template('header.html', listExt= allowed_extensions)})
    
@app.route('/changeUpPath',methods=["POST","GET"])
def changeUpPath():
    cur = mysql.connection.cursor()
    cur.execute("SELECT up_storePath  FROM `uploader_servers` WHERE up_id=1 ")
    data = cur.fetchall()
    cur.close()
    newPath=str(data[0]['up_storePath'])
    app.config['UPLOAD_FOLDER'] = newPath
     
@app.route('/Registration')
def Registration():
    return render_template("uploader/registration.html")

@app.route('/Contact')
def Contact():
    return render_template("uploader/contact.html")

@app.route('/About')
def About():
    return render_template("uploader/about.html")

@app.route("/Login",  methods=["GET","POST"])
def Login():
    if request.method == 'POST':
        username = str(request.form["lname"])
        password = request.form['lpass']
        curl = mysql.connection.cursor()
        curl.execute("SELECT * FROM users WHERE username='"+username+"' and password='"+ password+"'")
        user = curl.fetchone()
        curl.close()

        if user is None :
            msg='حطأ ادخال باسم المستخدم او كلمة المرور '
            return render_template("uploader/registration.html",msg=msg)  
        else:
            global userType
            userType=str(user["type"])
            changeUserAuth(userType)
            return redirect(url_for('Main'))
    else:
        return render_template("uploader/registration.html")

@app.route("/SignUp", methods=["GET","POST"])
def SignUp():
    if request.method == 'GET':
        return render_template("User/registration.html")
    else:
        name = request.form['lname']
        password = request.form['lpass']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (name, password))
        mysql.connection.commit()
        flash("تم اضفة حسابك بنجاح يمكنك الان تسجيل الدخول")
        return render_template("uploader/registration.html")

@app.route('/changeUserAuth/<userType>')
def changeUserAuth(userType='visitor'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` where f_groupType LIKE (%s)", (userType,))
    data = cur.fetchall()
    cur.close()
    global allowed_extensions,allowed_size,allowed_speedUp,allowedDown
    allowed_extensions.clear() 
    allowed_size.clear() 
    allowed_speedUp.clear() 
    allowedDown.clear() 
    for f in data:
      allowed_extensions.append(f['f_type'])
      allowed_size.append(float(f['f_size']))
      allowed_speedUp.append(f['f_speedUp'])
      allowedDown.append(f['f_speedDown'])

@app.route('/getAds')
def getAds():
    global adsTable
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `ads_table`")
    data = cur.fetchall()
    cur.close()
    for i in data:
        adsTable.append(i['ads_tag'])

@app.route("/ControlPanalLogin",  methods=["GET","POST"])
def ControlPanalLogin():
    global userType
    if userType=="admin":
        return redirect("http://185.229.119.49:3333/",code=302)

    if request.method == 'POST':
        username = str(request.form["username"])
        password = request.form['password']
        curl = mysql.connection.cursor()
        curl.execute("SELECT type FROM users WHERE username='"+username+"' and password='"+ password+"'")
        user = curl.fetchone()
        curl.close()
        userType=user['type']
        if user is None :
            return redirect(url_for('signUp'))        
        else:
            changeUserAuth(user['type'])
            if user['type']=="admin":
                return redirect("http://185.229.119.49:3333/",code=302)
            else:
                flash("ليس لديك صلاحية للوصول لهذة الصفحة")
                return render_template("admin_login.html") 
    else:
        return render_template("admin_login.html")


@app.route("/upload",methods=["POST","GET"])
def upload():
    msg0=' '
    msg1=' '
    msg3=' '
    filePath=' '
    today = datetime.today()
    if request.method == 'GET':
        redirect(url_for('Main'))
    else:
        file = request.files['file1']
        filename = secure_filename(file.filename)
        #file.seek(0, 2)
        #fSize = file.tell()
        #print(fSize)

        if file :
            #________________________Save file to uploader path
            file.save(app.config['UPLOAD_FOLDER'] + "/" + str(filename))  
            msg1  = 'File "' + file.filename + '" successfully uploaded to Store Path!'

            f_realName=file.filename
            fname = str(int.from_bytes(f_realName.encode('utf-8'), byteorder='big'))

            filePath=app.config['UPLOAD_FOLDER'] + "/" + str(fname) 
            filePath1=app.config['UPLOAD_FOLDER'] + "/" + str(f_realName) 
            stats=os.stat(filePath1)
            
            f_size=float(stats.st_size/1024) #KB
            f_type=f_realName.split('.')[-1]
            f_upDate=today
            
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""INSERT INTO `uploader_files` (`f_name`, `f_realName`, `f_size`, `f_type`, `f_upDate`)
                            VALUES (%s,%s,%s,%s,%s);""",[fname, f_realName, f_size, f_type, f_upDate])
            mysql.connection.commit()       
            cur.close()
            msg3 = 'File "' + str(f_realName) + '" successfully stored in the database as!' + fname
        else:
            flash(" يوجد خطأ بالتحميل اعد مرة اخرى")
    #return jsonify({'htmlresponse':render_template('uploader/response.html', msg0=msg0, msg1=msg1, msg3=msg3, filePath=filePath)})
    return render_template('uploader/response.html', msg0=msg0, msg1=msg1, msg3=msg3, filePath=filePath)



if __name__ == "__main__":
    app.run(debug=True)#host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 4444))
    
