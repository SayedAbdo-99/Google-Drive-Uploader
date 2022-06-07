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
from FileGDriveNew import DriveAPI

app = Flask(__name__)

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gd'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
userType='admin'
allowed_extensions = ["gif", "png", "jpg", "jpeg", "bmp", "zip", "rar","exe","ova"]
allowed_size, allowed_speedUp, allowedDown = [20971522097152, 22097152097152, 20971520971522, 20920971527152, 20920971527152, 20209715297152, 20920971527152,20920971527152,20920971527152],[],[]


@app.route('/')
def Run():
    #return redirect(url_for('Main'))
    #allowed_extensions, allowed_size, allowed_speedUp, allowedDown = changeUserAuth()
    #return render_template('uploader/uploadfile.html')
    #return render_template("index.html")
    return render_template("user/admin_users.html")

@app.route('/Main')
def Main():
    return render_template('uploader/main.html',exts=json.dumps(allowed_extensions),sizes=json.dumps(allowed_size))
    #jsonify({'htmlresponse': render_template('header.html', listExt= allowed_extensions)})

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
def changeUserAuth(userType='admin'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` where f_groupType LIKE (%s)", (userType,))
    data = cur.fetchall()
    cur.close()
    allowed_extensions.clear() 
    allowed_size.clear() 
    allowed_speedUp.clear() 
    allowedDown.clear() 
    for f in data:
      allowed_extensions.append(f['f_type'])
      allowed_size.append(float(f['f_size']))
      allowed_speedUp.append(f['f_speedUp'])
      allowedDown.append(f['f_speedDown'])

def allowed_file(filename,fileSize):
    extention =filename.split('.')[-1].lower()
    if extention in allowed_extensions:
        fileid=allowed_extensions.index(extention)
        print("allowed_file")
        print(fileSize)
        print(allowed_size[fileid])
        return (fileSize <= float(allowed_size[fileid]))
    else:
        return False
    

@app.route("/upload",methods=["POST","GET"])
def upload():
    msg=''
    msg0=''
    msg1=''
    msg2=''
    msg3=''
    filePath=''
    obj = DriveAPI()
    today = datetime.today()
    if request.method == 'GET':
        redirect(url_for('Main'))
    else:
        file = request.files['file1']
        #fTest=request.files['uploadFile']
        print(file)
        fSiz=100000000 #round(float(len(file.read())))
        filename = secure_filename(file.filename)
        
        print(fSiz)

        if file and allowed_file(file.filename,fSiz):
            file.save(app.config['UPLOAD_FOLDER'] + "/" + str(filename))  #os.path.join(app.config['UPLOAD_FOLDER'],filename))
            msg1  = 'File "' + file.filename + '" successfully uploaded to Store Path!'
            filePath=app.config['UPLOAD_FOLDER'] + "/" + str(filename)
            
            stats=os.stat(filePath)

            f_realName=file.filename
            fname = str(int.from_bytes(f_realName.encode('utf-8'), byteorder='big'))
            f_size=round(float(stats.st_size/1024))
            f_type=f_realName.split('.')[-1]
            f_upDate=today
            
            msg2= obj.FileUpload(filePath)
            
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""INSERT INTO `uploader` (`f_name`, `f_realName`, `f_size`, `f_type`, `f_upDate`)
                            VALUES (%s,%s,%s,%s,%s);""",[fname, f_realName, f_size, f_type, f_upDate])
            mysql.connection.commit()       
            cur.close()
            msg3 = 'File Data "' + file.filename + '" successfully stored in the database!'
            
            allfiles=obj.getAllFilesData()
            for f in allfiles:
                print(f)
                if f_realName == f['name']:
                    
                    gd_sizeKB=round(float(f['size'])/1024)

                    print(f['name'])
                    print(f['size'])
                    print(gd_sizeKB)
                    print(f_size)
                    print(filePath)

                    if f_size == gd_sizeKB:
                        msg0='The files are the same'
                        #os.remove(filePath)
                    else:

                        msg0='The files are different in size. please, upload file again'
            msg  = ' '
        else:
            msg  = 'Invalid Uplaod extension or size'
            filePath=' '
            flash(" هذا الامتدااد غير مسموح به او حجم املف كبير")
    
    return render_template('uploader/main.html', msg=msg, msg0=msg0, msg1=msg1, msg2=msg2, msg3=msg3, filenameimage=filePath)


#____________________________the control Panal _______________________

@app.route("/ControlPanalLogin",  methods=["GET","POST"])
def ControlPanalLogin():
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
                return redirect(url_for('Index'))
            else:
                flash("ليس لديك صلاحية للوصول لهذة الصفحة")
                return render_template("user/admin_login.html") 
    else:
        return render_template("user/admin_login.html")

@app.route('/Index')
def Index():
    #return render_template('uploader/uploadfile.html')
    return render_template("user/admin_users.html")


@app.route('/loadadmins')
def loadadmins():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `users` where type='admin'")
    data = cur.fetchall()
    cur.close()
    return render_template('user/admin_manage.html', admins=data)

@app.route('/loadclients')
def loadclients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `users` where type='client'")
    data = cur.fetchall()
    cur.close()
    print(len(data))
    return render_template('user/client_manage.html', clients=data)


@app.route('/getFileAuth/<gtype>')
def getFileAuth(gtype):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` where f_groupType LIKE (%s)", (gtype,))
    data = cur.fetchall()
    #print(data)
    cur.close()
    for file in data:
        su=file['f_speedUp']
        sd=file['f_speedDown']
        break
    return render_template('user/file_auth.html', files=data,speedUp=su,speedDown=sd, groupType=gtype)

@app.route('/delFileAuth/<string:id>/<gtype>', methods = ['GET'])
def delFileAuth(id,gtype):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `file_control` WHERE f_id=%s and f_groupType=%s", (id,gtype))
    mysql.connection.commit()
    flash("تم حذف الامتداد بنجاح ")
    return redirect(url_for('.getFileAuth',gtype=gtype))

@app.route('/updateFileAuth/<gtype>', methods = ['GET','Post'])
def updateFileAuth(gtype):
    if request.method == 'POST':
        speedUp = request.form['speedUp']
        speedDown = request.form['speedDown']
        filesLen = int(request.form['filesLen'])
        
        fileSizes=[]
        fileTypes=[]
        for i in range(1,filesLen+1):
            f_Type =request.form[str(i)]
            fileTypes.append(f_Type)
            fileSizes.append(str(request.form[str(f_Type)]))
        
        #fileType = request.form['fileType']

        cur = mysql.connection.cursor()
        for (ftype , size) in zip(fileTypes,fileSizes):
            cur.execute("""UPDATE `file_control` SET `f_size` = %s , f_speedUp =%s , f_speedDown =%s   
                    WHERE `f_type` = %s and f_groupType=%s;""", (size,speedUp,speedDown,ftype,gtype))
            mysql.connection.commit()
        flash("تم تعديل البيانات بنجاح  ")
    return redirect(url_for('.getFileAuth',gtype=gtype))

@app.route('/addFileAuth/<gtype>', methods=["GET","POST"])
def addFileAuth(gtype):

    if request.method == "POST":
        f_type=request.form['extisnew'] 
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `file_control` ( `f_type`,`f_groupType`)  VALUES (%s,%s)""", (f_type,gtype))
        mysql.connection.commit()
        flash("تمت اضافة الامتداد بنجاح")
    return redirect(url_for('.getFileAuth',gtype=gtype))
   

@app.route('/changeUpPath',methods=["POST","GET"])
def changeUpPath():
    if request.method == 'GET':
        return render_template("uploader/uploadPath.html")
    else:
        try:
            newPath=str(request.form['path'])
            app.config['UPLOAD_FOLDER'] = newPath
            msg1 = "change saved successfully to new path '"+newPath+"'!"
        except:
            msg1 = "sorry,change path  faild !"
        return render_template("uploader/uploadPath.html",msg1=msg1)

#____________________________the Google Driver Server Management _______________________
def updateGDAccounts(gd_id='1',credPath='credentials/credentials1.json'):
    obj = DriveAPI(gd_id,credPath)
    files =obj.getAllFilesData()
    size=0
    for file in files:
        size = size + float(file['size'])
    cur = mysql.connection.cursor()
    cur.execute("""
            UPDATE gdrive_accounts
            SET   filesNum=%s, usedSize=%s 
            WHERE gd_id=%s """, (len(files),float(size/1048576),gd_id))
    mysql.connection.commit()
    cur = mysql.connection.cursor()


@app.route('/getGDAccounts',methods=["GET","POST"])
def getGDAccounts():
    '''obj = DriveAPI()
    data =obj.getAllFilesData()'''
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `gdrive_accounts`")
    data1 = cur.fetchall()
    for account in data1:
        updateGDAccounts(account['gd_id'],account['credPath'])
        
    cur.execute("SELECT * FROM `gdrive_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("gdriveServers/gdserver_manage.html", gdServers=data)

@app.route('/gdControl',methods=["GET","POST"])
def gdControl():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `gdrive_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("gdrive/gdControl.html", accounts=data)

@app.route('/addGDServer',methods=["GET","POST"])
def addGDServer():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        #password = request.form['password']
        maxSize = request.form['maxSize']
        credPath = request.form['credPath']
        gd_order = request.form['gd_order']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `gdrive_accounts` (`username`, `email`, `maxSize`, `credPath`, `gd_order`) 
                    VALUES ( %s,%s,%s,%s,%s);""",(username, email, maxSize, credPath,gd_order))
        mysql.connection.commit()
        flash("تمت اضافة السيرفر بنجاح")
        return redirect(url_for('getGDAccounts'))

@app.route('/delGDServer/<gd_id>', methods = ['GET'])
def delGDServer(gd_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `gdrive_accounts` WHERE gd_id=%s ", (gd_id))
    mysql.connection.commit()
    flash("تم حذف الامتداد بنجاح ")
    return redirect(url_for('getGDAccounts'))

@app.route('/updateGDServer',methods=["GET","POST"])
def updateGDServer():
    if request.method == 'POST':
        gd_id = request.form['gd_id']
        username = request.form['username']
        email = request.form['email']
        maxSize = request.form['maxSize']
        credPath = request.form['credPath']
        gd_order = request.form['gd_order']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE `gdrive_accounts` SET `username` =%s, `email` =%s, `maxSize` = %s , `credPath` = %s, `gd_order` = %s
                         WHERE gd_id` = %s;
                         """,(username, email, maxSize, credPath, gd_order,gd_id))
        mysql.connection.commit()
        return redirect(url_for('getGDAccounts'))
   
if __name__ == "__main__":
    app.run(debug=True , port=5000)

