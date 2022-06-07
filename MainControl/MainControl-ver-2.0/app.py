from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from FileGDriveNew import DriveAPI


app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kl'

mysql = MySQL(app)





@app.route('/')
def Run():
    return render_template("index.html")

@app.route('/changeConfig')
def changeConfig(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB):
    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] =MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB


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
        updateGDAccounts(account[0],account[7])
        
    cur.execute("SELECT * FROM `gdrive_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("gdrive/gdReport.html", accounts=data)

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
        password = request.form['password']
        maxSize = request.form['maxVal']
        credPath = request.form['credPath']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `gdrive_accounts` (`username`, `email`, `password`, `maxSize`, `credPath`) VALUES ( %s,%s,%s,%s,%s);",(username, email, password, maxSize, credPath))
        mysql.connection.commit()
        return render_template("index.html")
    else:
        return render_template("gdrive/addGDServer.html")

@app.route('/getKlAccounts',methods=["GET","POST"])
def getKlAccounts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `kleeja_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("kleeja/klReport.html", accounts=data)

@app.route('/klControl',methods=["GET","POST"])
def klControl():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `kleeja_accounts`")
    data = cur.fetchall()
    cur.close()
    return render_template("kleeja/klControl.html", accounts=data)

@app.route('/addKlAccount',methods=["GET","POST"])
def addKlAccount():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_host = request.form['db_host']
        db_user = request.form['db_user']
        db_pass = request.form['db_pass']
        db_name = request.form['db_name']
        db_uploadPath = request.form['db_uploadPath']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `kleeja_accounts` ( `username`, `password`, `db_host`, `db_user`, `db_pass`, `db_name`, `db_uploadPath`) VALUES (%s,%s,%s,%s,%s,%s,%s);",(username, password, db_host, db_user, db_pass, db_name, db_uploadPath))
        mysql.connection.commit()
        return render_template("index.html")
    else:
        return render_template("kleeja/addKlAccount.html")

if __name__ == "__main__":
    app.run(debug=True)

'''
@app.route('/deleteEdara/<string:eid>', methods = ['GET'])
def deleteEdara(eid):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM edara WHERE e_id=%s", (eid,))
    mysql.connection.commit()
    return redirect(url_for('edara'))

@app.route("/addEdara", methods=["POST"])
def addEdara():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO edara (e_name, e_desc) VALUES (%s,%s)",(name,desc))
        mysql.connection.commit()
        return redirect(url_for('edara'))

@app.route('/updateEdara',methods=['POST','GET'])
def updateEdara():
    if request.method == 'POST':
        id_data = request.form['id']
        Name = request.form['name']
        desc = request.form['desc']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE edara
               SET   e_name=%s, e_desc=%s 
               WHERE r_id=%s
            """, (Name,desc,id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('edara'))

#_____________________region
@app.route('/region',methods=["GET","POST"])
def region():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT r_id, r_name,e_name, r_desc  
                   FROM region LEFT JOIN edara
                   ON edara.e_id = region.edara_id
                   """)
    data = cur.fetchall()
    cur.close()
    return render_template("region.html", region=data)

@app.route('/deleteRegion/<string:rid>', methods = ['GET'])
def deleteRegion(rid):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM region WHERE r_id=%s", (rid,))
    mysql.connection.commit()
    return redirect(url_for('region'))

def getMaxID(tableName):
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(r_id) FROM "+tableName)
    data1 = cur.fetchall()



@app.route("/addRegion", methods=["POST"])
def addRegion():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(r_id) FROM region ")
        data1 = cur.fetchall()
        r_id= data1[0]
        name = request.form['name']
        desc = request.form['desc']
        cur.execute("""SELECT e_name  FROM region LEFT JOIN edara
                   ON edara.e_id = region.edara_id
                   """)
        data2 = cur.fetchall()
        
        
        data = cur.fetchall()
        rid=data[0]
        
        edara_id=request.form['edara_id']
       
        cur.execute("INSERT INTO region (r_id, r_name, r_desc,edara_id) VALUES (%s,%s,%s,%s)",(rid,name,desc,edara_id))
        mysql.connection.commit()
        return redirect(url_for('region'))

@app.route('/updateRegion',methods=['POST','GET'])
def updateRegion():
    if request.method == 'POST':
        id_data = request.form['id']
        Name = request.form['name']
        desc = request.form['desc']
        edara_id=request.form['edara_id']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE edara
               SET   e_name=%s, e_desc=%s, edara_id=%s 
               WHERE e_id=%s
            """, (Name,desc,edara_id,id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('region'))

'''
