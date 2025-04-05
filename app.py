from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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