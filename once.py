# Run when there is no database
from app import app, db

with app.app_context():
    db.create_all()