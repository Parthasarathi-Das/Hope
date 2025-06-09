'''Server Side Logic'''
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hope
import os

# Important Declaration
app = Flask(__name__)
app.config["SECRET_KEY"] ="Partha"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
mymail ="abc312967@gmail.com"
pw ="partha1223"

# Table For Visitors
class Visit(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    visitor_email  = db.Column(db.String(50), nullable = False)
    visitor_name = db.Column(db.String(200), nullable = False)
    stock = db.Column(db.String(20), nullable = False)
    days = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, default = datetime.now())
    def __repr__(self):
        return f"{self.sno} - {self.visitor_email} - {self.time}"

# Table For Feedbacks
class Feedback(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(200), nullable = False)
    user_email  = db.Column(db.String(50), nullable = False)
    desc  = db.Column(db.String(500), nullable = False)
    rate = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, default = datetime.now())
    def __repr__(self):
        return f"{self.sno} - {self.user_email} - {self.time}"

# Method For running The Deep Learning Prediction in Background
async def run_dl(stock, days):
    pred_df = hope.predict_stock(stock, days)
    return pred_df

# Default Route
@app.route('/')
def index():
    return render_template('index.html')

# Predictor Page
@app.route('/predictor')
def predictor():
    return render_template('predictor.html')

# Beginning The Process of Prediction
@app.route('/startpredict', methods =['POST','GET'])
def startpredict():
    stock = request.form['ticker']
    email = request.form['email']
    name = request.form['name']
    days = request.form['days']
    if email == '':                                             # When email is not entered
        return render_template('predictor.html', no_email = 1)
    elif name == '':                                            # When username is not entered
        return render_template('predictor.html', no_name = 1)
    elif stock == '':                                           # When stock ticker is not entered
        return render_template('predictor.html', no_ticker = 1)
    elif days == '':                                            # When number od days is not entered
        return render_template('predictor.html', no_day = 1)
    days = int(days)
    valid = hope.ticker_validate(stock)
    if valid:                                                   # When the stock ticker is valid
        data = [stock, days, email, name, stock, days]
        session["input_data"] = data
        return render_template('wait.html')
    else:                                                       # When the stock ticker is invalid
        return render_template("predictor.html", notfound = 1)

# Running The Process of Prediction in background
@app.route('/run_dl', methods =['POST','GET'])
async def run_ml_method():
    data = session.get('input_data')
    pred_df = await run_dl(data[0], data[1])
    record =  Visit(visitor_email = data[2], visitor_name = data[3], stock = data[4], days = data[5])
    db.session.add(record)
    db.session.commit()
    return render_template("dashboard.html", data = pred_df.values)

# Making the Graph Plot
@app.route('/Plot')
def plot():
    return render_template('plot.html')

# Feedback Page
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

# Saving The Feedback
@app.route('/savefeedback',methods =["POST","GET"])
def savefeedback():
    name = request.form["name"]
    email = request.form["email"]
    desc = request.form["desc"]
    rate = request.form["rate"]
    if name == '':                                              # When name is not entered
        return render_template('feedback.html', no_name = 1)
    elif email == '':                                           # When email is not entered
        return render_template('feedback.html', no_email = 1)
    elif desc == '':                                            # When description is not entered
        return render_template('feedback.html', no_desc = 1)
    elif rate == '':                                            # When rating is not entered
        return render_template('feedback.html', no_rate = 1)
    rate = int(rate)
    visitor = Visit.query.filter_by(visitor_email = email).all() # Cecking if the user has used the predictor or not
    print(visitor)
    if visitor == []:
        return render_template('feedback.html', invalid_feedback = 1)
    record = Feedback(user_name = name, user_email = email, desc = desc, rate = rate)
    db.session.add(record)
    db.session.commit()
    return render_template('feedback.html', success =1)

# Administrative View
@app.route('/admin')
def admin():
    return render_template('admin.html',authorized =0)

# Verifiction of Admin
@app.route('/verify',methods =['POST','GET'])
def verify():
    email = request.form["email"]
    password = request.form["password"]
    if (email == mymail and password == pw):
        visits = Visit.query.all()
        feedbacks = Feedback.query.all()
        return render_template('admin.html', authorized =1, visit = visits, feedback = feedbacks)
    else:
        return render_template('admin.html',authorized =0, intruder = 1)

# About The Website
@app.route('/site')
def site():
    return render_template('site.html')

# About Our Team
@app.route('/team')
def team():
    return render_template('team.html')

# The Main Function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port= int(os.environ.get("PORT",5000)))