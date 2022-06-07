from importlib.metadata import files
from importlib.resources import path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from FileGDrive import DriveAPI



app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kl'

mysql = MySQL(app)


@app.route('/')
def Run():
    return redirect(url_for('login'))


@app.route('/Index')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, real_filename FROM `klj_files` ")
    data1 = cur.fetchall()
    cur.execute("SELECT * FROM `getfromgdrive` ")
    data2 = cur.fetchall()
    data=data1 + data2
    cur.close()
    return render_template('index.html', files=data)


@app.route("/login",  methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = str(request.form["username"])
        password = request.form['password']
        curl = mysql.connection.cursor()
        curl.execute("SELECT * FROM users WHERE username='"+username+"' and password='"+ password+"'")
        user = curl.fetchone()
        curl.close()

        if user is None :
            return redirect(url_for('signUp'))
                
        else:
            return redirect(url_for('Index'))
    else:
        return render_template("User/login.html")

@app.route("/signUp", methods=["GET","POST"])
def signUp():
    if request.method == 'GET':
        return render_template("User/registration.html")
    else:
        name = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)",(name,password))
        mysql.connection.commit()
        return redirect(url_for('login'))
    
@app.route('/upFile/<string:filePath>', methods = ['GET'])
def upFile(filePath):
    obj = DriveAPI()
    print(filePath)
    FileStorePath="C:/xampp/htdocs/kl/uploads/"
    fullPath=str(FileStorePath+filePath)
    obj.FileUpload(fullPath)
    return redirect(url_for('Index'))

@app.route('/downFile/<id>&<name>')
def downFile(id,name):
    obj = DriveAPI()
    FileStorePath="C:/xampp/htdocs/kl/uploads/"
    fullPath=str(FileStorePath+str(name))
    obj.FileDownload(id,fullPath)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO getfromgdrive (fileID, fileName) VALUES (%s,%s)",(str(id),str(name),))
    mysql.connection.commit()
    return redirect(url_for('Index'))


@app.route('/getFilesData/')
def getFilesData():
    obj = DriveAPI()
    data =obj.getAllFilesData()
    return render_template("DownloadFile.html",filesData=data)



'''

@app.route('/about')
def about():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `products` ")
    data = cur.fetchall()
    cur.close()
    return render_template('about.html', products=data)

@app.route('/loadproduct', methods = ['GET'])
def loadproduct():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products ")
    data = cur.fetchall()
    cur.close()
    return render_template('admin/allProducts.html', products=data)

@app.route('/productList')
def productList():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products ")
    data = cur.fetchall()
    cur.close()
    return render_template('admin/crud_products.html', products=data)

@app.route('/addPro', methods=["GET","POST"])
def addPro():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        Pid=request.form['id']
        name = request.form['name']
        price = request.form['price']
        details = request.form['details']
        imagePath = request.form['imagePath']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `products` (`id`, `name`, `price`, `details`, `image`) VALUES (%s,%s,%s,%s,%s)", (Pid, name,price,details,imagePath))
        mysql.connection.commit()
        return redirect(url_for('productList'))
    else:
        return render_template('admin/addProduct.html')

@app.route('/deletePro/<string:pid>', methods = ['GET'])
def deletePro(pid):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (pid,))
    mysql.connection.commit()
    return redirect(url_for('productList'))

@app.route('/updatePro',methods=['POST','GET'])
def updatePro():
    if request.method == 'POST':
        id_data = request.form['id']
        proName = request.form['proName']
        price = request.form['price']
        details = request.form['details']
        imgPath = request.form['imgPath']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE products
               SET   name=%s, price=%s, details=%s, image=%s 
               WHERE id=%s
            """, (proName,price, details,imgPath,id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('productList'))


@app.route('/Uesrs')
def Uesrs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Users ")
    data = cur.fetchall()
    cur.close()
    return render_template('admin/crud_users.html', users=data)


@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        id=request.form['id']
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        feedback = request.form['feedback']
        password = request.form['password']
        type = request.form['type']
        image =request.form['image']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (u_id,name,address,phone,feedback,password,u_type,image) VALUES (%s, %s, %s,%s, %s,%s, %s, %s)", (id, name,address,phone,feedback,password,type, image))
        mysql.connection.commit()
        return redirect(url_for('Uesrs'))




@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE u_id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Uesrs'))



@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['h_id']
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        type = request.form['type']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE users
               SET  name=%s, address=%s, phone=%s, u_type=%s 
               WHERE u_id=%s
            """, (name,address, phone, type,id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Uesrs'))

@app.route("/checkUser", methods=["POST"])
def check():
    username = str(request.form["username"])
    password = str(request.form["password"])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM user WHERE name ='" + username + "'")
    user = cursor.fetchone()

    if len(user) is 1:
        return redirect(url_for("home"))
    else:
        return "failed"
'''


if __name__ == "__main__":
    app.run(debug=True)
