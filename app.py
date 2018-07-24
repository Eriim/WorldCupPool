from functools import wraps
from flask import Flask, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import datetime




app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:devils@localhost:5432/WCP_DB'
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(25))
    email=db.Column(db.String(120), unique=True)
    password=db.Column(db.String(25))

    def __init__(self, username, email, password):
        self.username=username
        self.email=email
        self.password=password
class Group(db.Model):
    __tablename__="group"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))

    def __init__(self, name):
        self.name=name
class Team(db.Model):
    __tablename__="team"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))
    group_id=db.Column(db.Integer, ForeignKey('group.id'))
    wins=db.Column(db.Integer)
    losses=db.Column(db.Integer)
    draws=db.Column(db.Integer)
    goalsfor=db.Column(db.Integer)
    goalsagainst=db.Column(db.Integer)

    def __init__(self, name, group_id):
        self.name=name
        self.group_id=group_id
class Match(db.Model):
    __tablename__="match"
    id=db.Column(db.Integer, primary_key=True)
    team1_id=db.Column(db.Integer, ForeignKey('team.id'))
    team2_id=db.Column(db.Integer, ForeignKey('team.id'))
    score1=db.Column(db.Integer)
    score2=db.Column(db.Integer)
    date=db.Column(db.Date)

    def __init__(self, team1_id, team2_id, score1, score2, date):
        self.team1_id=team1_id
        self.team2_id=team2_id
        self.score1=score1
        self.score2=score2
        self.date=date
class Prediction(db.Model):
    __tablename__="prediction"
    id=db.Column(db.Integer, primary_key=True)
    match_id=db.Column(db.Integer, ForeignKey('match.id'))
    user_id=db.Column(db.Integer, ForeignKey('user.id'))
    prediction1=db.Column(db.Integer)
    prediction2=db.Column(db.Integer)
    date=db.Column(db.Date)

    def __init__(self, match_id, user_id, prediction1, prediction2, date):
        self.match_id=match_id
        self.user_id=user_id
        self.prediction1=prediction1
        self.prediction2=prediction2
        self.date=date
class Pool(db.Model):
    __tablename__="pool"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))
    date=db.Column(db.Date)
    password=db.Column(db.String(50))

    def __init__(self, name, date, password):
        self.name=name
        self.date=date
        self.password=password
class PoolUsers(db.Model):
    __tablename__="poolusers"
    id=db.Column(db.Integer, primary_key=True)
    pool_id=db.Column(db.Integer, ForeignKey('pool.id'))
    user_id=db.Column(db.Integer, ForeignKey('user.id'))
    score=db.Column(db.Integer)
    date=db.Column(db.Date)

    def __init__(self, pool_id, user_id, score, date):
        self.pool_id=pool_id
        self.user_id=user_id
        self.score=score
        self.date=date

class Standing():
    def __init__(self, username, score, position):
        self.username=username
        self.score=score
        self.position=position




def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        user_id= session.get('user_id')
        if user_id:
            user = db.session.query(User).filter(User.id==user_id).first()
            if user:
                return function_to_protect(*args, **kwargs)
            else:
                flash("Session exists, but user does not exist in database")
                return redirect(url_for('login'))
        else:
            flash("Please log in")
            return redirect(url_for('login'))


@app.route("/")
def index():
    return render_template("login.html")
@app.route("/createAccount", methods=['POST'])
def success():
    if request.method=='POST':
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        confirm=request.form["confirm"]

        print(request.form)
        if db.session.query(User).filter(User.email == email).count()== 0 and db.session.query(User).filter(User.username == username).count()== 0:
            user=User(username, email, password)
            db.session.add(user)
            db.session.commit()
            return render_template("success.html", text="Account successfully created")
        return render_template("createUser.html", text="That email address OR username is already in use please select another")
@app.route("/login", methods=['POST'])
def login():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]
        verifyUser=db.session.query(User).filter(User.username==username).first()
        if verifyUser.password == password:
            session['userId'] = verifyUser.id
            return render_template("index.html")
    return render_template("login.html", text="Whoops, something went wrong please try again")
# ChoosePool Loads the pool selection page.
@app.route("/choosePool")
def choosePool():
    data = db.session.query(Pool).all()
    return render_template("choosePool.html", data=data)
@app.route("/createUser")
def createUser():
    return render_template("createUser.html")
@app.route("/selectPool", methods=['POST'])
def selectPool():
    if request.method=='POST':
        id=request.form["id"]
        password=request.form["password"]
        verifypassword=db.session.query(Pool).filter(Pool.id==id).first()
        if verifypassword.password == password:
            now=datetime.datetime.now()

            userId= session.get('userId')
            poolUser = PoolUsers(id, userId, 0, now)
            db.session.add(poolUser)
            db.session.commit()

            return render_template("success.html", text=id)

    return render_template("error.html", text=id)
@app.route("/logout", methods=['POST'])
def logout():
    if request.method=='POST':
        session.clear()
        return render_template("/index.html")
@app.route("/groupStagePicks")
def groupStagePicks():
    return render_template("groupStage.html")
@app.route("/groupStagePrediction", methods=['POST'])
def gsPrediction():
    if request.method=='POST':
        userId=session.get('userId')
        now=datetime.datetime.now()
        i = 1
        k = 2
        matchCounter = 1
        while matchCounter < 49:
            prediction1=request.form[str(i)]
            prediction2=request.form[str(k)]
            i += 2
            k += 2
            prediction = Prediction(matchCounter, userId, prediction1, prediction2, now)
            db.session.add(prediction)
            matchCounter += 1
        db.session.commit()
        return render_template("/success.html", text="Congratulations on making your group stage predictions.")
@app.route("/viewStandings", methods=['POST'])
def viewStandings():
    if request.method=='POST':
        pool=db.session.query(Pool).filter(Pool.id==request.form['id']).first()

        poolusers = db.session.query(PoolUsers).filter(PoolUsers.pool_id==pool.id).order_by(PoolUsers.score).all()
        standingList = list()
        counter=1
        for pu in poolusers:
            id=pu.user_id
            user = db.session.query(User).filter(User.id==id).first()
            print(user.username)
            standing = Standing(user.username, pu.score, counter)
            standingList.append(standing)
            counter+=1
        return render_template("viewStandings.html", data=standingList, title=pool.name)
@app.route("/querytest")
def querytest():
    poolId=1
    poolusers = db.session.query(User).join(PoolUsers).filter(PoolUsers.pool_id==poolId).order_by(PoolUsers.score).all()
    users = list()
    for pu in poolusers:
        print(users)



    return render_template("viewStandings.html", data=poolusers)

if __name__ == '__main__':
    app.secret_key='A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.debug=True

    app.run()
