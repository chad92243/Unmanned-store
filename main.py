import myFunction
from flask import Flask, render_template, Response, request, jsonify, session
from flask_socketio import SocketIO
import camera
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ayush'
app.config['UPLOAD_FOLDER'] = 'static/files'
Socketio = SocketIO(app)

#for face_login.html
@app.route('/video_stream')
def video_stream():
    return Response(camera.gen_frames(Socketio), mimetype='multipart/x-mixed-replace; boundary=frame')

#for train.html
@app.route('/train_screen')
def train_screen():
    return Response(camera.register_video(Socketio), mimetype='multipart/x-mixed-replace; boundary=frame')

#-------------------------------------------------------
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('index.html')

@app.route("/webcam", methods=['GET','POST'])
def webcam():
    session.clear()
    return render_template('shoppingCar.html')

@app.route('/webapp')
def webapp():
    return Response(camera.video_detection(Socketio), mimetype='multipart/x-mixed-replace; boundary=frame')


#-------------------------------------------------------

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/train')
def train():
    return render_template('train.html')

@app.route('/face_login')
def face_login():
    return render_template('faceLogin.html')

#傳參數username & 餘額 到shoppingCar頁面
@app.route('/shoppingCar/<username>')
def shoppingCar(username):

    data = myFunction.read_SQL(mydb="topics", table="account_info")
    balance = 0
    for i in range(len(data)):
        if (data[i][1] == username):
            balance = data[i][2]

    return render_template('shoppingCar.html', username = username, balance = balance)

#from login.html / 登入成功->shoppingCar.html  失敗->login.html
@app.route('/login_with_password', methods = ['POST', 'GET'])
def login_with_password():
    
    account = request.form['account']
    password = request.form['password']
    
    userCheck = False

    data = myFunction.read_SQL(mydb="topics", table="person")
    for i in range(len(data)):
        if(account == data[i][1] and password == data[i][2]):
            userCheck = True
    
    data2 = myFunction.read_SQL(mydb="topics", table="account_info")
    balance = None
    if (data[i][1] == account):
        balance = data2[i][2]

    if(userCheck == True):
        return render_template('shoppingCar.html', username = account, balance = balance)
    else:
        return render_template('login.html', message = "wrong account or password")


#from register.html / 註冊成功->train.html  失敗->register.html
@app.route('/check_account', methods = ['POST', 'GET'])
def check_account():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        haveAcoount = False

        data = myFunction.read_SQL(mydb="topics", table="person")

        
        for i in range(len(data)):
            if(account == data[i][1] and password == data[i][2]):
                haveAcoount = True
        
        if(haveAcoount == True):
            return render_template('register.html', register_message = "already have account")
        else:
            myFunction.update_person(mydb="topics", table="person", account=account, password=password, email=email, phone=phone)
            return render_template('train.html')


@app.route('/deduction', methods = ['POST', 'GET'])
def deduction():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        data = myFunction.read_SQL(mydb="topics", table="account_info")
        account = request.form['username']
        cost = request.form['total_cost']

        balance = 0
        for i in range(len(data)):
            if (data[i][1] == account):
                balance = data[i][2]
        
        if(int(balance) >= int(cost)):
            myFunction.update_balance(balance=balance, cost=cost, username=account)
            return render_template('checkout.html', message = "扣款成功")
        else:
            return render_template('checkout.html', message = "扣款失敗 請確認餘額")



if __name__ == '__main__':
    Socketio.run(app, debug=True)


