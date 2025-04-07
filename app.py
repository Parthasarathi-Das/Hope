from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hope

app = Flask(__name__)
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

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/site')
def site():
    return render_template('site.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/predictor')
def predictor():
    return render_template('predictor.html')
if __name__ == "__main__":
    app.run(debug=True, port= 8000)