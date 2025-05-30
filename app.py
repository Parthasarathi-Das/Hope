from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hope
import os

app = Flask(__name__)
app.config["SECRET_KEY"] ="Partha"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
mymail ="abc312967@gmail.com"
pw ="partha1223"

class Visit(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    visitor_email  = db.Column(db.String(50), nullable = False)
    visitor_name = db.Column(db.String(200), nullable = False)
    stock = db.Column(db.String(20), nullable = False)
    days = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, default = datetime.now())
    def __repr__(self):
        return f"{self.sno} - {self.visitor_email} - {self.time}"

class Feedback(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(200), nullable = False)
    user_email  = db.Column(db.String(50), nullable = False)
    desc  = db.Column(db.String(500), nullable = False)
    rate = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, default = datetime.now())
    def __repr__(self):
        return f"{self.sno} - {self.user_email} - {self.time}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predictor')
def predictor():
    return render_template('predictor.html')

async def run_dl(stock, days):
    pred_df = hope.predict_stock(stock, days)
    return pred_df


@app.route('/startpredict', methods =['POST','GET'])
def startpredict():
    stock = request.form['ticker']
    email = request.form['email']
    name = request.form['name']
    days = request.form['days']
    if email == '':
        return render_template('predictor.html', no_email = 1)
    elif name == '':
        return render_template('predictor.html', no_name = 1)
    elif stock == '':
        return render_template('predictor.html', no_ticker = 1)
    elif days == '':
        return render_template('predictor.html', no_day = 1)
    days = int(days)
    valid = hope.ticker_validate(stock)
    if valid:
        data = [stock, days, email, name, stock, days]
        session["input_data"] = data
        return render_template('wait.html')
    else:
        return render_template("predictor.html", notfound = 1)

@app.route('/run_dl', methods =['POST','GET'])
async def run_ml_method():
    data = session.get('input_data')
    pred_df = await run_dl(data[0], data[1])
    record =  Visit(visitor_email = data[2], visitor_name = data[3], stock = data[4], days = data[5])
    db.session.add(record)
    db.session.commit()
    # prediction_dict = pred_df.to_dict(orient='records')
    return render_template("dashboard.html", data = pred_df.values)

@app.route('/Plot')
def plot():
    return render_template('plot.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/savefeedback',methods =["POST","GET"])
def savefeedback():
    name = request.form["name"]
    email = request.form["email"]
    desc = request.form["desc"]
    rate = request.form["rate"]
    if name == '':
        return render_template('feedback.html', no_name = 1)
    elif email == '':
        return render_template('feedback.html', no_email = 1)
    elif desc == '':
        return render_template('feedback.html', no_desc = 1)
    elif rate == '':
        return render_template('feedback.html', no_rate = 1)
    rate = int(rate)
    visitor = Visit.query.filter_by(visitor_email = email).all()
    print(visitor)
    if visitor == []:
        return render_template('feedback.html', invalid_feedback = 1)
    record = Feedback(user_name = name, user_email = email, desc = desc, rate = rate)
    db.session.add(record)
    db.session.commit()
    return render_template('feedback.html', success =1)

@app.route('/admin')
def admin():
    return render_template('admin.html',authorized =0)

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

@app.route('/site')
def site():
    return render_template('site.html')

@app.route('/team')
def team():
    return render_template('team.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port= int(os.environ.get("PORT",5000)))