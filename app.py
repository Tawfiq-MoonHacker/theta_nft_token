from flask import Flask,flash, render_template, redirect, url_for,request,session
from flask_restful import Api,Resource
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import get_contracts as gc


from dateutil.relativedelta import relativedelta
import sqlite3
import timeago
import email_validator
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import smtplib

from create_token import create_contract
import secrets

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from file import forgot_password1,verification_email,return_username
import pymysql
from math import floor

from credentials import email_user, email_password

import time
import os 
import threading

import json
from web3 import Web3
import time 

from sqlalchemy import create_engine


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['UPLOAD_FOLDER'] = 'static/imgs'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

theta_network = "https://eth-rpc-api.thetatoken.org/rpc"


def moveDecimalPoint(num, decimal_places):
    for _ in range(abs(decimal_places)):

        if decimal_places>0:
            num *= 10; #shifts decimal place right
        else:
            num /= 10.; #shifts decimal place left

    return float(num)


s = URLSafeTimedSerializer('Thisisasecret!')


def send(subject,content,file,email_send):
    
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject
    

    msg.attach(MIMEText(content,'html'))
    
    
    if file != None:
        filename= file
        attachment  =open(filename,'rb')
    
        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+filename)
    
        msg.attach(part)
        
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)
    
    
    server.sendmail(email_user,email_send,text)
    server.quit()
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    address = db.Column(db.String(4000),unique = True)
    private_address = db.Column(db.String(4000),unique = True)
    balance = db.Column(db.Float,default = 0.000000)
    token = db.Column(db.String(2000),default = None)
    verification = db.Column(db.Boolean,default = False)
    public_api = db.Column(db.String(2000),default = '0')
    api_secret = db.Column(db.String(2000),default= '0')
    
class Contracts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(2000),unique=False)
    contract_address = db.Column(db.String(4000),unique = False)
    address = db.Column(db.String(4000),unique=False)
    owner = db.Column(db.Boolean,default = False)
    price = db.Column(db.Float)
    sell  = db.Column(db.Boolean,default = False)
    quantity = db.Column(db.Integer,default = 0)
    
    
# {api_secret: "", "to_address" : "" ,"quantity": 1}
class transfer_api(Resource):
    def post(self,public_api):
        user = User.query.filter_by(public_api = public_api).first()
        
        
        try:
            if user.api_secret == request.form['api_secret']:

                w3 = Web3(Web3.HTTPProvider(theta_network))

                balance = w3.eth.get_balance(user.address)
                if balance > int(request.form['quantity']):
                    gc.transfer_coins(user.address,request.form['to_address'],user.private_address,int(request.form['quantity']))
        except:
            return {"failed":500}
        
        return {"success":200}

api.add_resource(transfer_api,"/transfering/<string:public_api>")


# {'api_secret':'','name':'','symbol','','supply':10000,'price':0.001,'sell_quantity':1,'img_file' :f}
class create_token_api(Resource):
    def post(self,public_api):
        user = User.query.filter_by(public_api = public_api).first()
        
        try:
            if user.api_secret == request.form['api_secret']:
                file = request.files['img_file']
            
                if file.filename == '':
                    flash('No selected file')
                    return {"failed":500}
                
                # if file and allowed_file(file.filename):
                #     filename = secure_filename(file.filename)
                #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
                path = os.path.join(app.config['UPLOAD_FOLDER'], request.form['symbol']+".png")
                file.save(path)
            
                contract_address = create_contract(request.form['symbol'],request.form['name'],request.form['supply'],user.address)
            
                if float(request.form['sell_quantity']) == 0:
                    contract = Contracts(username = current_user.username,contract_address = contract_address,address = user.address,owner = True ,price = float(request.form['price']),sell = False,quantity = 0)
                    db.session.add(contract)
                    db.session.commit()
                    
                else:
                    contract = Contracts(username = current_user.username,contract_address = contract_address,address = user.address,owner = True ,price = float(request.form['price']) ,sell = True,quantity = int(request.form['sell_quantity']))
                    db.session.add(contract)
                    db.session.commit()

                
        except:
            return {"failed":500}
        
        return {"success":200}

api.add_resource(create_token_api,"/creating/<string:public_api>")

# {api_secret: "", "name" : " name_token" ,"sell_quantity": 1,'price':0.0001}
class tokens_api(Resource):
    def post(self,public_api):
        try:        
            user = User.query.filter_by(public_api = public_api).first()
            dict1 = {'own_tokens' : []}
            
            if user.api_secret == request.form['api_secret']:
                contract = Contracts.query.filter_by(username = user.username).all()
                dict2 = {'name' : gc.get_name(user.address,contract.contract_address),'symbol':gc.get_symbol(user.address,contract.contract_address),'price':contract.price,'sell_quantity' : contract.quantity,'balance' : gc.get_balance(user.address,contract.contract_address),'image':'/image/' + gc.get_symbol(user.address,contract.contract_address) }
                dict1['own_tokens'].append(dict2)
                
            return dict1
        
        except:
            return {"failed":500}
        
    
    def put(self,public_api):
        user = User.query.filter_by(public_api = public_api).first()
        
        try:
            if user.api_secret == request.form['api_secret']:
                contract = Contracts.query.filter_by(username = user.username).all()
                for i in contract:
                    if request.form['name'] == gc.get_name(user.address,contract.contract_address):
                        
                        contract.price = float(request.form['price'])
                        contract.quantity = int(request.form['quantity_sell'])
                        db.session.commit()
                            
                    
        except:
            return {"failed":500}
        
        return {"success":200}

api.add_resource(tokens_api,"/my_token_details/<string:public_api>")

# {api_secret: ""}
class tokens_av(Resource):
    def post(self,public_api):
        try:        
            user = User.query.filter_by(public_api = public_api).first()
            dict1 = {'tokens' : []}
            
            if user.api_secret == request.form['api_secret']:
                contract = Contracts.query.all()
                dict2 = {'name' : gc.get_name(user.address,contract.contract_address),'symbol':gc.get_symbol(user.address,contract.contract_address),'price':contract.price,'sell_quantity' : contract.quantity,'balance' : gc.get_balance(user.address,contract.contract_address),'image':'/image/' + gc.get_symbol(user.address,contract.contract_address) }
                dict1['tokens'].append(dict2)
                
            return dict1
        
        except:
            return {"failed":500}
    
api.add_resource(tokens_av,"/token_details/<string:public_api>")




@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    
    
    if user:         
        try:

            w3 = Web3(Web3.HTTPProvider(theta_network))

            #it checks if there is a payment
            balance = w3.eth.get_balance(user.address)
            user.balance = moveDecimalPoint(balance,-18)
            db.session.commit()
            
        except Exception as e:
            print(e)
            pass
        
    return User.query.get(int(user_id))

    
  
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login(username = None):
    form = LoginForm()
    
    if username != None:
        user = User.query.filter_by(username = username).first()
        login_user(user)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) and user.verification == True:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
    if request.method == 'POST':
        
        user = User.query.filter_by(email = form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data) and user.verification == True:
                login_user(user,remember=form.remember.data)
                return redirect(url_for('dashboard'))
            
            if user.verification == False:
                token = s.dumps(user.email, salt='email-confirm')
                
                link = url_for('confirm_email', token=token, _external=True)
                
                user.token = token
                
                db.session.commit()
        
                content = verification_email(link)
                subject = "here is your verification "
            
                send(subject, content,None,form.email.data)
                
                return render_template("verify-email.html")
            
            
            return render_template('login.html',form = form,wrong = True)
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form,wrong = False)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        
        w3 = Web3(Web3.HTTPProvider(theta_network))
        
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')

        acct = w3.eth.account.create()
        public_api = secrets.token_urlsafe(18)
        api_secret = secrets.token_urlsafe(18)
        
        
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,token=token,verification = False,public_api = '0',api_secret = '0')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,address = acct.address,private_address = acct.key.hex(),balance = 0.0000000 ,token=token,verification = False,public_api = public_api,api_secret = api_secret)

        db.session.add(new_user)
        db.session.commit()
        
        
        # paying = Payments(username = form.username.data, payment = 0,address = address,confirm = False,start_date = datetime.today(),end_date = datetime.today())
        # db.session.add(paying)
        # db.session.commit()


        link = url_for('confirm_email', token=token, _external=True)


        content = verification_email(link)
        subject = "here is your verification "
    
        send(subject, content,None,form.email.data)
        
        return render_template("verify-email.html")
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html',form = form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    user = User.query.filter_by(token = token).first()
    user.verification = True
    
    db.session.commit()

    return login(username = user.username)

@app.route('/forgot_password',methods=['POST','GET'])
def forgot_password():
    if request.method == 'POST':
        
        email = request.form['email']
        token = s.dumps(email, salt='reset-password')
        
        try:
            user = User.query.filter_by(email = email).first()
            user.token = token
            db.session.commit()
        except:
            return render_template("forgot_password.html")
        
        
        
        link = url_for('reset_password', token=token, _external=True)
        content =  forgot_password1(link)
        subject = "reset your password"
    
        send(subject, content,None,email)
        
        return render_template("link_sent.html")
        
    return render_template("forgot_password.html")

@app.route('/forgot_username',methods=['POST','GET'])
def forgot_username():
    if request.method == 'POST':
        
        email = request.form['email']
        token = s.dumps(email, salt='reset-password')
        name = ""
        
        try:
            user = User.query.filter_by(email = email).first()
            name = user.username
            db.session.commit()
        except:
            return render_template("forgot_username.html")
        
        
        
        content =  return_username(name)
        subject = "Username Reveal"
    
        send(subject, content,None,email)
        
        return render_template("link_sent.html")
        
    return render_template("forgot_username.html")


@app.route('/reset_password/<token>',methods=['POST','GET'])
def reset_password(token,link = None):
    
    form = LoginForm()
        
    if request.method == 'POST':
        user = User.query.filter_by(token = token).first()
        if user:
            user.password = generate_password_hash(form.password.data, method='sha256')
            db.session.commit()
            return login(user.username)
        
    if request.method == 'GET':
        user = User.query.filter_by(token = token).first()
        try:
            email = s.loads(token, salt='reset-password', max_age=300)
            link = url_for('reset_password', token=token, _external=True)
            return render_template("reset_password.html",link = link,form = form)

        except SignatureExpired:
            return '<h1>The token is expired!</h1>'
    


@app.route('/dashboard')
@login_required
def dashboard():
    # payment = Payments.query.filter_by(username = current_user.username).first()
    # now = datetime.today() - relativedelta(days = 1)
    # now = payment.end_date
    
    return render_template('dashboard.html', name=current_user.username)


@app.route('/dashboard/payments')
@login_required
def payment():
    
    name = current_user.username
        
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    balance = user.balance
    
    return render_template('payments.html',name = name,balance = balance,theta_address = address)
    


@app.route('/transfer',methods=['POST','GET'])
@login_required
def transfer():
    
    user = User.query.filter_by(username = current_user.username).first()
    # payment = Payments.query.filter_by(username = current_user.username).first()
    private_address = user.private_address
    address_send = user.address
    
    
    if request.method == 'POST':
        quantity = float(request.form['quantity'])
        address_recv = request.form['address']
        
        gc.transfer_coins(address_send,address_recv,private_address,float(quantity))
    
        return redirect(url_for('dashboard'))
    else:
        return render_template('transfer.html',name = current_user.username)

    


@app.route('/create_token',methods=['POST','GET'])
@login_required
def create_token():
    
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    
    name = ""
    symbol = ""
    supply = ""
    
    if request.method == 'POST':
        try:
            
            if 'file' not in request.files:
                print('there is no file1 in form!')
                
            symbol = request.form['symbol']
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            # if file and allowed_file(file.filename):
            #     filename = secure_filename(file.filename)
            #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            path = os.path.join(app.config['UPLOAD_FOLDER'], symbol+".png")
            file.save(path)
            
            # sell = request.form['sell']
            name = request.form['name']
            supply = float(request.form['supply'])
            price = float(request.form['price'])
            
            # if 'yes' in sell:
            #     sell = True
            # else:
            #     sell = False
            
            # address = "0x5114e874A0182AD0D0783B9F20986fb6d0dae5d2"

            contract_address = create_contract(symbol,name,supply,address)
            
            
            contract = Contracts(username = current_user.username,contract_address = contract_address,address = address,owner = True ,price = price,sell = False,quantity = 0)

            
            db.session.add(contract)
            db.session.commit()
            
        
        except Exception as e:
            print(e)
            pass
        
    

    
    return render_template("create_token.html",name = user.username)


@app.route('/tokens',methods=['POST','GET'])
@login_required
def tokens():
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    
    
    # address = "0x5114e874A0182AD0D0783B9F20986fb6d0dae5d2"
    contract = Contracts.query.filter_by().all()
    contract_address = []
    prices = []
    symbols = []
    names = []
    balances = []
    id_number = []
    
    for i in contract:
        if i.sell == True and i.username != current_user.username:
            # contract_address.append(i.contract_address)
            prices.append(i.price)
            # names.append(gc.get_name(address,i.contract_address))
            balances.append(i.quantity)
            symbols.append(gc.get_symbol(address,i.contract_address))
            id_number.append(i.id)
    
    basket = []
    for i in range(len(prices)):
        list1 = []
        list1.append('imgs/' + symbols[i] + '.png')
        list1.append(symbols[i])
        list1.append(prices[i])
        list1.append(id_number[i])
        list1.append(balances[i])
        basket.append(list1)
    
    return render_template("tokens.html",name = user.username,basket = basket,id_number = id_number)


@app.route('/tokens/<sym>/<id_number>',methods=['POST','GET'])
@login_required
def tokens_sym(sym,id_number):
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    
    if request.method == 'GET':
        # address = "0x5114e874A0182AD0D0783B9F20986fb6d0dae5d2"
        contract = Contracts.query.filter_by().all()
        contract_address = ""
        price = 0
        symbol = ""
        name_token = ""
        balance = 0
        quantity = 0
        
        for i in contract:
            if i.sell == True and gc.get_symbol(address,i.contract_address) == sym:
                # contract_address.append(i.contract_address)
                price = i.price
                name_token = gc.get_name(address,i.contract_address)
                symbol = gc.get_symbol(address,i.contract_address)
                quantity = i.quantity
        
        path = 'imgs/' + symbol + '.png'
        
        
        return render_template("description_token.html",name = user.username,path = path,symbol=symbol,name_token = name_token,quantity = quantity,own = False,price = price,id_number = id_number)
    
    elif request.method == 'POST':
        quantity = int(request.form['quantity'])
        address_send = ""
        contract = Contracts.query.filter_by(id = id_number).all()
        
        price = 0
        contract_address = ''
        balance = 0
        quantity_available = 0
        
        for i in contract:
            price = float(i.price)
            address_send = i.address
            contract_address = i.contract_address
            end_price = quantity * float(i.price)
            quantity_available = i.quantity
        
        if quantity_available < quantity:
            return tokens_sym(sym,id_number)
        
        user = User.query.filter_by(username = current_user.username).first()
        
        address_recv = ""
        username = ""
        
        if user:
            
            address_recv = user.address
            private_address = user.private_address
            
            #if the balance is not enough to buy the tokens
            if user.balance < end_price:
                return "not enough balance of theta"
            
            else:
                #checking if the user has the token from before
                passed = False
                contract_check = Contracts.query.filter_by(username = current_user.username).all()
                for i in contract_check:
                    if i.contract_address == contract_address:
                        passed = True
                
                contract = Contracts.query.filter_by(id = id_number).all()
                i.quantity = quantity_available - quantity
                db.session.commit()
                
                if not passed:
                    new_contract = Contracts(username = user.username,contract_address = contract_address,address =user.address,owner = True,price=0.0,sell = False,quantity=0)
                    db.session.add(new_contract)
                    
                    db.session.commit()
                    
                gc.transfer_coins(address_recv,address_send,private_address,end_price)
                
                try:
                    result = gc.transfer(address_send,address_recv,int(quantity),contract_address)
                except Exception as e:
                    print(e)
                    return "it could not transfer tokens for lack of TFuel (gas)"
                
                contract = Contracts.query.filter_by(id = id_number).first()
                contract.quantity = quantity_available - quantity
                if contract.quantity == 0:
                    contract.sell = False
                
                db.session.commit()
                
                return redirect(url_for('my_tokens'))
        
        

@app.route('/my_tokens/<string:sym>',methods=['POST','GET'])
@login_required
def my_tokens_sym(sym):
    
    # address = "0x5114e874A0182AD0D0783B9F20986fb6d0dae5d2"
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    
    if request.method == 'GET':
        
        contract = Contracts.query.filter_by(username = current_user.username).all()
        contract_address = ''
        price = 0
        symbol = ''
        name_token = ''
        balances = 0
        quantity = 0
        sell = False
        
        for i in contract:
            if gc.get_symbol(address,i.contract_address) == sym:
                # contract_address.append(i.contract_address)
                price = i.price
                name_token = gc.get_name(address,i.contract_address)
                balance = gc.get_balance(address,i.contract_address)
                
                symbol  = gc.get_symbol(address,i.contract_address)
                quantity = i.quantity
                sell = i.sell
        
        path = 'imgs/' + symbol + '.png'
        return render_template("description_token.html",name = user.username,path=path,symbol = symbol,price = price, quantity =quantity,sell = sell,balance = balance,own = True,name_token = name_token)
    
    
    
    else:
        
        if request.form.get('submit') == 'submit':
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            
            contract = Contracts.query.filter_by(username = current_user.username).all()
           
            for i in contract:
                if gc.get_symbol(address,i.contract_address) == sym:
                    i.price = price
                    i.quantity = quantity 
                    i.sell = True
                    db.session.commit()
                    break
                
            return redirect(url_for('my_tokens'))
        
        if request.form.get('submit') == 'cancel':
            
            contract = Contracts.query.filter_by(username = current_user.username).all()
            
            for i in contract:
                if gc.get_symbol(address,i.contract_address) == sym:
                    i.quantity = 0
                    i.sell = False
                    db.session.commit()
                    break
                
            return redirect(url_for('my_tokens'))

@app.route('/my_tokens',methods=['POST','GET'])
@login_required
def my_tokens():
    user = User.query.filter_by(username = current_user.username).first()
    address = user.address
    
    
    # address = "0x5114e874A0182AD0D0783B9F20986fb6d0dae5d2"
    contract = Contracts.query.filter_by(username = current_user.username).all()
    contract_address = []
    prices = []
    symbols = []
    names = []
    balances = []
    
    for i in contract:
            # contract_address.append(i.contract_address)
            prices.append(i.price)
            # names.append(gc.get_name(address,i.contract_address))
            # balances.append(gc.get_balance(address,i.contract_address))
            symbols.append(gc.get_symbol(address,i.contract_address))
    
    basket = []
    for i in range(len(prices)):
        list1 = []
        list1.append('imgs/' + symbols[i] + '.png')
        list1.append(symbols[i])
        list1.append(prices[i])
        basket.append(list1)
    
    return render_template("my_tokens.html",name = user.username,basket = basket)


@app.route('/api')
@login_required
def api():
    user = User.query.filter_by(username = current_user.username).first()
    
    if user:
        public_api = user.public_api
        secret_api = user.api_secret
        
        return render_template('api.html',name = current_user.username, public_api = public_api,secret_api = secret_api)
    else:
        return "nothing is there"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/image/<symbol>')
def image(symbol):
    path = 'imgs/' + symbol + '.png'
    
    return render_template('image.html',path,symbol)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.run(debug=True)





