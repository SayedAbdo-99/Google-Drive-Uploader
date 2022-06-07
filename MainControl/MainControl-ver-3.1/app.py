from http import client
from tabnanny import check
from flask import Flask, render_template, request, jsonify,redirect, url_for, flash
from flask_mysqldb import MySQL,MySQLdb #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from FileGDrive import DriveAPI

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
allowed_extensions, allowed_size, allowed_speedUp, allowedDown = [],[],[],[]

@app.route('/')
def Run():
    allowed_extensions, allowed_size, allowed_speedUp, allowedDown = changeUserAuth()
    return redirect(url_for('main'))
    #return render_template('uploader/uploadfile.html')
    #return render_template("user/admin_users.html")
    #return render_template("uploader/uploadPath.html")

@app.route('/')
def changeUserAuth(userType='admin'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` where f_groupType LIKE (%s)", (userType,))
    data = cur.fetchall()
    cur.close()
    allowed_extensions, allowed_size, allowed_speedUp, allowedDown=[],[],[],[]
    for f in data:
      allowed_extensions.append(f['f_type'])
      allowed_size.append(f['f_size'])
      allowed_speedUp.append(f['f_speedUp'])
      allowedDown.append(f['f_speedDown'])
      
    return allowed_extensions, allowed_size, allowed_speedUp, allowedDown
        

def allowed_file(filename,fileSize):
    extention =filename.rsplit('.', 1)[-1].lower()
    fileid=allowed_extensions.index(extention)
    return ('.' in filename) and (extention in allowed_extensions) and (fileSize >= float(allowed_size[fileid]))




@app.route('/main')
def main():
    #return render_template('uploader/uploadfile.html')
    return render_template("user/admin_users.html")


@app.route("/login",  methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = str(request.form["username"])
        password = request.form['password']
        curl = mysql.connection.cursor()
        curl.execute("SELECT type FROM users WHERE username='"+username+"' and password='"+ password+"'")
        user = curl.fetchone()
        print(user)
        curl.close()
        userType=user['type']
        if user is None :
            return redirect(url_for('signUp'))
                
        else:
            if user['type']=="admin":
                changeUserAuth(user['type'])
                return redirect(url_for('main'))
            else:
                return redirect(url_for('upload'))

    else:
        return render_template("user/login.html")

@app.route("/signUp", methods=["GET","POST"])
def signUp():
    if request.method == 'GET':
        return render_template("user/registration.html")
    else:
        name = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)",(name,password))
        mysql.connection.commit()
        return redirect(url_for('login'))

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
'''
@app.route("/checkFileInfo",methods=["POST","GET"])
def checkFileInfo(gd_FileID,sotrePath):
    obj = DriveAPI()
    allfiles=obj.getAllFilesData()
    for file in allfiles:
        if file['id']==gd_FileID:
            gd_FileInfo=file
    store_FileInfo=os.stat(sotrePath)
    if gd_FileInfo['size']==store_FileInfo.st_size:
        return True

        msg="The files are the same"
        file.remove()
    else:
        msg="The files are different in size. please, upload file again"
        return False
'''

@app.route("/upload",methods=["POST","GET"])
def upload():
    obj = DriveAPI()
    today = datetime.today()
    if request.method == 'GET':
        return render_template("uploader/uploadfile.html")
    else:
        file = request.files['uploadFile']
        print(file)
    filename = secure_filename(file.filename)
    
    if file and allowed_file(file.filename):
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        msg1  = 'File "' + file.filename + '" successfully uploaded to Store Path!'
        filePath=app.config['UPLOAD_FOLDER'] + "/" + str(filename)
        stats = os.stat(filePath)
    

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
        msg0=''
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
    
    return jsonify({'htmlresponse': render_template('uploader/response.html', msg=msg, msg0=msg0, msg1=msg1, msg2=msg2, msg3=msg3, filenameimage=f_realName)})

@app.route('/getFileAuth')
def getFileAuth():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` ") #where f_groupType LIKE (%s)", ('f_groupType',))
    data = cur.fetchall()
    print(data)
    cur.close()
    return render_template('user/file_auth.html', files=data)

@app.route('/delFileAuth/<string:id>', methods = ['GET'])
def delFileAuth(id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `file_control` WHERE f_id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('getFileAuth'))

@app.route('/addFileAuth', methods=["GET","POST"])
def addFileAuth():

    if request.method == "POST":
        f_type=request.form['extisnew'] 
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `file_control` ( `f_type`)  VALUES (%s)""", (f_type,))
        mysql.connection.commit()
        flash("Data Inserted Successfully")
    return redirect(url_for('getFileAuth'))
    

if __name__ == "__main__":
    app.run(debug=True)
