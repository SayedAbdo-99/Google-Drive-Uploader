from flask import Flask, render_template, request, jsonify,redirect, url_for, flash
from flask_mysqldb import MySQL,MySQLdb
#from sqlalchemy import true #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from FileGDriveNew import DriveAPI
import os

app = Flask(__name__)

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gd'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = '/root/flask_app/Uploader/Uploader-ver-4.3/static/uploads'
GoogleDriverID=1
userType='visitor'
allowed_extensions = []#["gif", "png", "jpg", "jpeg", "bmp", "zip", "rar","exe","ova"]
allowed_size = []#[20971522097152, 22097152097152, 20971520971522, 20920971527152, 20920971527152, 20209715297152, 20920971527152,20920971527152,20920971527152]
allowed_speedUp, allowedDown = [],[]

#____________________________the control Panal _______________________

@app.route('/')
def Run():
    return redirect(url_for('Index'))
    #allowed_extensions, allowed_size, allowed_speedUp, allowedDown = changeUserAuth()
    #return render_template('uploader/uploadfile.html')
    #return render_template("index.html")
    #return render_template("user/admin_users.html")

@app.route('/changeUpPath',methods=["POST","GET"])
def changeUpPath():
    cur = mysql.connection.cursor()
    cur.execute("SELECT up_storePath  FROM `uploader_servers` WHERE up_id=1 ")
    data = cur.fetchall()
    cur.close()
    if data is not None:
        newPath=str(data[0]['up_storePath'])
        app.config['UPLOAD_FOLDER'] = newPath      

@app.route('/changeGoogleDriverID')
def changeGoogleDriverID():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `gdrive_accounts` ORDER BY gd_order")
    data = cur.fetchall()
    global GoogleDriverID
    for account in data:
        if float(account['maxSize']) > float(account['usedSize']):
            GoogleDriverID=data[0]['gd_id']
    cur.close()

@app.route('/Index')
def Index():
    changeUpPath()
    changeGoogleDriverID()
    
    #return render_template('uploader/uploadfile.html')
    return redirect(url_for('getGroups'))


@app.route('/addGroup', methods=["GET","POST"])
def addGroup():
    if request.method == "POST":
        g_name=request.form['g_name'] 
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `groups` (`g_name`)  VALUES (%s)""", (g_name,))
        mysql.connection.commit()
        flash("تمت اضافة المجموعة بنجاح")
    return redirect(url_for('getGroups'))

@app.route('/delGroup/<g_id>', methods = ['GET'])
def delGroup(g_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `groups` WHERE g_id=%s", (g_id))
    mysql.connection.commit()
    flash("تم حذف المجموعة بنجاح ")
    return redirect(url_for('getGroups'))

@app.route('/updateGroup',methods=["GET","POST"])
def updateGroup():
    if request.method == 'POST':
        g_id = request.form['g_id']
        g_name = request.form['g_name']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE `groups` SET `g_name` =%s
                                 WHERE g_id = %s; """,( g_name,g_id))
        mysql.connection.commit()
        flash("تم تعديل المجموعة بنجاح ")
        return redirect(url_for('getGroups'))

@app.route('/getGroups')
def getGroups():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `groups`")
    data = cur.fetchall()
    cur.close()
    return render_template("user/admin_users.html", groups=data)


@app.route('/loadGroup/<g_name>')
def loadGroup(g_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `users` where type=%s",g_name)
    data = cur.fetchall()
    cur.close()
    print(len(data))
    return render_template('user/group_manage.html', clients=data)


@app.route('/loadadmins')
def loadadmins():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `users` where type='admin'")
    data = cur.fetchall()
    cur.close()
    return render_template('user/admin_manage.html', admins=data)

#_______________________________________Ext 
@app.route('/getFileAuth/<gtype>')
def getFileAuth(gtype):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `file_control` where f_groupType LIKE (%s)", (gtype,))
    data = cur.fetchall()
    #print(data)
    cur.close()
    su=0
    sd=0
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
   

#____________________________the Google Driver Server Management _______________________
def updateGDAccounts(gd_id='1'):
    obj = DriveAPI(gd_id)
    files =obj.getAllFilesData()
    size=0
    for file in files:
        #print(file)
        size = size + float(file['size'])
    #print('Account '+str(gd_id)+' SizeKB: '+ str(size) )
    #print('Account '+str(gd_id)+' SizeGB Stored on DB: '+ str(float(size/1048576)))
    
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
        updateGDAccounts(account['gd_id'])
        
    cur.execute("SELECT * FROM `gdrive_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("gdriveServers/gdserver_manage.html", gdServers=data)

@app.route('/addGDServer',methods=["GET","POST"])
def addGDServer():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        #password = request.form['password']
        maxSize = request.form['maxSize'] #GB
        gd_order = request.form['gd_order']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `gdrive_accounts` (`username`, `email`, `maxSize`, `gd_order`) 
                    VALUES ( %s,%s,%s,%s);""",(username, email, maxSize,gd_order))
        mysql.connection.commit()
        flash("تمت اضافة السيرفر بنجاح")
        return redirect(url_for('getGDAccounts'))

@app.route('/delGDServer/<gd_id>', methods = ['GET'])
def delGDServer(gd_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `gdrive_accounts` WHERE gd_id=%s ", (gd_id))
    mysql.connection.commit()
    flash("تم حذف السيرفر بنجاح ")
    return redirect(url_for('getGDAccounts'))

@app.route('/updateGDServer',methods=["GET","POST"])
def updateGDServer():
    if request.method == 'POST':
        gd_id = request.form['gd_id']
        username = request.form['username']
        email = request.form['email']
        maxSize = request.form['maxSize']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE `gdrive_accounts` SET `username` =%s, `email` =%s, `maxSize` = %s
                                 WHERE gd_id = %s; """,(username, email, maxSize,gd_id))
        mysql.connection.commit()
        
        return redirect(url_for('getGDAccounts'))

@app.route('/updateGDServerOrder/<int:ServersNumber>',methods=["GET","POST"])
def updateGDServerOrder(ServersNumber=0):
    if request.method == 'POST':
        for i in range(1,ServersNumber+1):
            gd_order = request.form[str('gd_order_'+str(i))]
            gd_id = request.form[str('gd_id_'+str(i))]
            
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE `gdrive_accounts` SET `gd_order` = %s
                            WHERE gd_id = %s; """,(gd_order,gd_id))
            mysql.connection.commit()
        changeGoogleDriverID()
        return redirect(url_for('getGDAccounts'))


#____________________________the Uploader Server Management _______________________

@app.route('/getUPAccounts',methods=["GET","POST"])
def getUPAccounts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `uploader_servers`")
    data = cur.fetchall()
    cur.close()
    return render_template("uploadServers/uploader_manage.html", upServers=data)

@app.route('/addUPServer',methods=["GET","POST"])
def addUPServer():
    if request.method == 'POST':
        up_name = request.form['up_name']
        up_order = request.form['up_order']
        up_storePath = request.form['up_storePath']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `uploader_servers` (`up_name`, `up_order`, `up_storePath`) 
                    VALUES ( %s,%s,%s);""",(up_name, up_order, up_storePath))
        mysql.connection.commit()
        flash("تمت اضافة السيرفر بنجاح")
        return redirect(url_for('getUPAccounts'))

@app.route('/delUPServer/<up_id>', methods = ['GET'])
def delUPServer(up_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `uploader_servers` WHERE up_id=%s ", (up_id))
    mysql.connection.commit()
    flash("تم حذف السيرفر بنجاح ")
    return redirect(url_for('getUPAccounts'))

@app.route('/updateUPServer',methods=["GET","POST"])
def updateUPServer():
    if request.method == 'POST':
        up_id = request.form['up_id']
        up_name = request.form['up_name']
        up_storePath = request.form['up_storePath']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE `uploader_servers` SET `up_name` =%s, `up_storePath` =%s
                                 WHERE up_id = %s; """,(up_name, up_storePath,up_id))
        mysql.connection.commit()
    changeUpPath()
    return redirect(url_for('getUPAccounts'))

@app.route('/updateUPServerOrder/<int:ServersNumber>',methods=["GET","POST"])
def updateUPServerOrder(ServersNumber=0):
    if request.method == 'POST':
        for i in range(1,ServersNumber+1):
            up_order = request.form[str('up_order_'+str(i))]
            up_id= request.form[str('up_id_'+str(i))]
            
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE `uploader_servers` SET `up_order` = %s
                            WHERE up_id = %s; """,(up_order,up_id))
            mysql.connection.commit()
    changeUpPath()
    return redirect(url_for('getUPAccounts'))

@app.route('/getUPFiles',methods=["GET"])
def getUPFiles():
    ServersID  = request.args.get('ServersID', '1')
    store_state  = request.args.get('store_state', '0')
    msg=''
    cur = mysql.connection.cursor()
    if store_state=='3':
        cur.execute("SELECT * FROM `uploader_files` where uploader_id=%s",(ServersID))
        msg='جميع الملفات'
    else:
        cur.execute("SELECT * FROM `uploader_files` where uploader_id=%s and store_state=%s ",(ServersID,store_state))
        if store_state=='0':
            msg='الملفات المخزنة على سيرفر التحميل'
        elif store_state=='1':
            msg='الملفات المخزنة على جوجل دريف '
        else:
            msg='الملفات المخزنة على سيرفر التحميل و جوجل دريف '
            
    data = cur.fetchall()
    cur.close()
    flash(msg)
    return render_template("uploadServers/files_manage.html", files=data,upserver_id=ServersID)

@app.route('/delUPServerFiles/<upserver_id>', methods = ['GET','POST'])
def delUPServerFiles(upserver_id='1'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `uploader_files` where uploader_id=%s and store_state=2 ",(upserver_id,))
    data = cur.fetchall()
    cur.close()
    for file in data:
        filePath=app.config['UPLOAD_FOLDER'] +'/'+str(file['f_realName'])
        os.remove(filePath)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""UPDATE `uploader_files` SET `store_state` = '1' 
        WHERE `uploader_files`.`f_id` =%s """,(str(file['f_id']),))
        mysql.connection.commit()       
        cur.close()
    flash('تم حذف الملفات من سيرفر التحميل بنجاح')
    return redirect(url_for('getUPFiles',ServersID=upserver_id,store_state=1))

@app.route('/compareFilesGDrive/<upserver_id>', methods = ['GET','POST'])
def compareFilesGDrive(upserver_id='1'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `uploader_files` where uploader_id=%s and store_state=2 ",(upserver_id,))
    data = cur.fetchall()
    cur.close()

    obj = DriveAPI(GoogleDriverID)
    gdFiles=list(obj.getAllFilesData())

    #gdFilesSize=[]
    #FilesSize=[]
    suc=[]
    fl=[]
    gdFileSize=0
    for file in data:
        #os.getcwd().replace('/','\\')
        filePath=app.config['UPLOAD_FOLDER'] +'/'+str(file['f_realName'])
        #FilesSize.append(file.stat(filePath).st_size)
        FileSize=os.stat(filePath).st_size
        for f in gdFiles:
            if f["name"] == file["f_realName"]:
                gdFileSize=float(f['size'])
                break

        #gdFilesSize.append(gdFileSize)
        if float(FileSize) == gdFileSize:
            suc.append(file['f_id'])
        else:
            fl.append(file['f_id'])

    #print(gdFilesSize)
    #print(FilesSize)

    flash('الملفات المتشابه:'+str(suc)+'  \n  الملفات المختلفة:'+str(fl))
    return redirect(url_for('getUPFiles',ServersID=upserver_id,store_state=1))


@app.route("/uploadFilesGDrive/<upserver_id>",methods=["POST","GET"])
def uploadFilesGDrive(upserver_id='1'):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `uploader_files` where uploader_id=%s and store_state=0",(upserver_id,))
    data = cur.fetchall()
    cur.close()
    msg2=''

    obj = DriveAPI(GoogleDriverID)
    for file in data:
        filePath=app.config['UPLOAD_FOLDER'] +'/'+str(file['f_realName'])
        msg2= obj.FileUpload(filePath)

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""UPDATE `uploader_files` SET `store_state` = '2' 
        WHERE `uploader_files`.`f_id` =%s """,(str(file['f_id']),))
        mysql.connection.commit()       
        cur.close()
    flash(msg2)
    return redirect(url_for('getUPFiles',ServersID=upserver_id,store_state=0))

#____________________________the Ads Management _____________________
@app.route('/getAds',methods=["GET","POST"])
def getAds():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `ads_table`")
    data = cur.fetchall()
    cur.close()
    return render_template("ads/ads_manage.html", adsTable=data)

@app.route('/addAds',methods=["GET","POST"])
def addAds():
    if request.method == 'POST':
        ads_id = request.form['ads_id']
        ads_tag = request.form['ads_tag']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO `ads_table` (`ads_id`, `ads_tag`) 
                    VALUES ( %s,%s);""",(ads_id, ads_tag))
        mysql.connection.commit()
        flash("تمت اضافة الاعلان بنجاح")
        return redirect(url_for('getAds'))

@app.route('/delAds/<ads_id>', methods = ['GET'])
def delAds(ads_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM `ads_table` WHERE ads_id=%s ", (ads_id))
    mysql.connection.commit()
    flash("تم حذف الاعلان بنجاح ")
    return redirect(url_for('getAds'))

@app.route('/updateAds',methods=["GET","POST"])
def updateAds():
    if request.method == 'POST':
        ads_id = request.form['ads_id']
        ads_tag = request.form['ads_tag']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE `ads_table` SET `ads_id` =%s, `ads_tag` =%s
                                 WHERE ads_id = %s; """,(ads_id, ads_tag,ads_id))
        mysql.connection.commit()
        flash("تم تعديل الاعلان بنجاح ")
        return redirect(url_for('getAds'))

if __name__ == "__main__":
     app.run(debug=True,host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 3333)))
