from functools import wraps
from flask import Flask, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import datetime

now=datetime.datetime.now()
print(now)

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

    def __init__(self, name, date):
        self.name=name
        self.date=date
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
    return render_template("error.html")
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
            return render_template("groupStage.html")
    return render_template("login.html", text="Whoops, something went wrong please try again")
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

        return render_template("success.html", text=id)


if __name__ == '__main__':
    app.debug=True
    app.run()
