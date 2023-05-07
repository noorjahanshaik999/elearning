from flask import Flask,redirect,request,render_template,url_for,flash,session,send_file,make_response
#from flask_mysqldb import MySQL
import mysql.connector
from flask_session import Session
from otp import genotp
from adminotp import adotp
from cmail import sendmail
from adminmail import adminsendmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from admintokenreset import admintoken
from io import BytesIO
app=Flask(__name__)
app.secret_key='hfbfe78hjef'
db=os.environ['RDS_DB_NAME']
user=os.environ['RDS_USERNAME']
password=os.environ['RDS_PASSWORD']
host=os.environ['RDS_HOSTNAME']
port=os.environ['RDS_PORT']
mydb=mysql.connector.connect(host=host,user=user,password=password,db=db,port=port)
with mysql.connector.connect(host=host,user=user,password=password,db=db,port=port) as conn:
    cursor=conn.cursor()
     cursor.execute("CREATE TABLE signup(username varchar(30) NOT NULL,mobile bigint DEFAULT NULL,email varchar(70) DEFAULT NULL,password varchar(40) DEFAULT NULL,PRIMARY KEY (username))")
     cursor.execute("CREATE TABLE profile(username varchar(30) DEFAULT NULL,score int DEFAULT NULL,course varchar(10) DEFAULT NULL,KEY username(username),FOREIGN KEY (username) REFERENCES signup(username))")
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        cursor.execute('select mobile from signup')
        edata=cursor.fetchall()
        #print(data)
        if (mobile, ) in edata:
            flash('User already exisit')
            return render_template('signup.html')
        if (email, ) in data:
            flash('Email id already exisit')
            return render_template('signup.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
    else:
        return render_template('signup.html')    
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from signup where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/Shome')
def home():
    return render_template('index.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('home'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<name>/<mobile>/<email>/<password>',methods=['GET','POST'])
def otp(otp,name,mobile,email,password):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            lst=[name,mobile,email,password]
            query='insert into signup values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            name=request.form['name']
            mobile=request.form['mobile']
            email=request.form['email']
            password=request.form['password']
            cursor=mysql.connection.cursor()
            email=session.get('user')
            cursor.execute('insert into signup(name,mobile,email,password) values(%s,%s,%s,%s)',[name,mobile,email,password])
            cursor=mydb.cursor(buffered=True)
            cursor.close()
            flash(f'{email} added successfully')
            return redirect(url_for('noteshome'))
        return render_template('home1.html')
    else:
        return redirect(url_for('login'))
@app.route('/forgetpassword',methods=['GET','POST'])
def forgetpassword():
    if request.method=='POST':
        email=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from signup where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset password for {data}'
            body=f'reset the password using -{request.host+url_for("createpassword",token=token(email,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user email'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        email=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update signup set password=%s where email=%s',[npass,email])
                cursor=mydb.cursor(buffered=True)
                return 'Password reset successfull'
            else:
                return 'password mismatch'
        return render_template('newpassword.html')
    except:
        return 'link expired try again'

@app.route('/javamaterial/')
def javamaterial():
    return render_template('javamaterial.html')
@app.route('/javacourse/')
def javacourse():
    return render_template('javacourse.html')
@app.route('/pythonmaterial/')
def pythonmaterial():
    return render_template('pythonmaterial.html')
@app.route('/pythoncourse/')
def pythoncourse():
    return render_template('pythoncourse.html')
@app.route('/javaquiz/')
def javaquiz():
    return render_template('javaquiz.html')

questions = [
    {
        'question': 'Python is Released in the year ? ',
        'options': ['1991', '1881', '1995', '2005'],
        'answer': '1991'
    },
    {
        'question': 'Extension Used to Save Python File ?',
        'options': ['.py', '.python', '.pythonfile', '.html'],
        'answer': '.py'
    },
    {
        'question': 'Type() Function is Used to ?',
        'options': ['Defines type of language', 'defines type of Variable', 'calculate Length ov Variable', 'None'],
        'answer': 'defines type of Variable'
    },
    {
        'question':'Python Keywords Can also be used as Variable Names ?',
        'options':['No','Yes','Can be Used in some Cases','Non'],
        'answer':'No'
    },
    {
        'question':'What is the output of following Python code ? print(0.1 + 0.2 == 0.3)',
        'options':['Error','Error','False','True'],
        'answer':'False'
    },
    {
        'question':'Which of the following items are present in the function header ?',
        'options':['function name','parameter list','Both the above','return value'],
        'answer':'Both the above'
    },
    {
        'question':'What is a recursive function ?',
        'options':['A function that calls other function',' A function which calls itself','Both the above',' None of the above'],
        'answer':'A function which calls itself'
    },
    {
        'question':' In which part of memory does the system stores the parameter and local variables of function call ?',
        'options':['stack','heap','Uninitialized data segment','Uninitialized data segment'],
        'answer':'stack'
    },
    {
        'question':'Which one of the following is the correct way of calling a function ?',
        'options':['function_name()','call function_name()','return function_name()','get function_name()'],
        'answer':'function_name()'
    },
    {
        'question':'Which of the following data types is not supported in python ?',
        'options':['List','Generics','Dictionary','Tuple'],
        'answer':'Generics'
    },
    # {
    #     'question':'What is the default value of encoding in encode() ?',
    #     'options':['ascii','ascii','utf-16','utf-8'],
    #     'answer':'utf-8'
    # },
    # {
    #     'question':'Which of these in not a core datatype ?',
    #     'options':['Class','Tuples','Dictionary','Lists' ],
    #     'answer':'Class'
    # }
    # Add more questions here
]

@app.route('/pqindex')
def pqindex():
    return render_template('pqindex.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Retrieve the user's answers from the form data
        user_answers = {}
        for key, value in request.form.items():
            if key != 'submit':
                user_answers[key] = value
        
        # Compare the user's answers to the correct answers in the questions list
        score = 0
        for question in questions:
            if user_answers.get(question['question']) == question['answer']:
                score += 1  
        if score>=6:
            username=session.get('user')
            cursor=mysql.connection.cursor()
            cursor.execute("insert into profile(username,score,course)values(%s,%s,'python')",[username,score])
            data=cursor.fetchone()
            mydb.commit()
            cursor.close()
        # Display the user's score and any incorrect answers
        return render_template('score.html', score=score, total=len(questions), user_answers=user_answers, questions=questions)
    else:
        # Shuffle the questions and select 5 random questions
        random.shuffle(questions)
        selected_questions = questions[:10]
        
        return render_template('quiz.html', questions=selected_questions)
@app.route('/certificate/')
def certificate():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute("select username,email from signup where username=%s",[session.get('user')])
        data=cursor.fetchone()
        mydb.commit()
        cursor.close()
        return render_template('certificate.html',data=data)
@app.route('/certificatedownload/')
def certificatedownload():
    cursor=mysql.connection.cursor()
    cursor.execute("select username,email from signup where username=%s",[session.get('user')])
    data=cursor.fetchone()
    mydb.commit()
    cursor.close()
    certificate=render_template('certificate.html',data=data)
    response=make_response(certificate)
    response.headers.set('Content-Disposition','attachmaent',filename='certificate.html')
    response.headers.set('Content-Type','text')
    return response
@app.route('/profile',methods=["GET","POST"])
def profile():     
    cursor=mysql.connection.cursor()
    cursor.execute('select username,score,course from profile where username=%s',[session.get('user')])
    data=cursor.fetchone()
    print(data)
    cursor.connection.commit()
    cursor.close()
    return render_template('profile.html',data=data)

app.run(use_reloader=True,debug=True)
