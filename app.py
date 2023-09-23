from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config["SECRET_KEY"] = "HAHAIDK"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/')
def homepage():
    return render_template('index.html', app_name='BulkBois', description='For the GymBros')

@app.route('/create_tables')
def create_tables():
    with app.app_context():
        db.create_all()
    return 'Database tables created successfully!'

if __name__ == '__main__':
    app.run()
























class Memebers(db.Model):
    id = db.Column('member_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    address = db.Column(db.String(200))  # Corrected spelling to 'address'
    pin = db.Column(db.String(10))
    phone_number = db.Column(db.String(15))  # Assuming a simple string for phone number
    email = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    member_since = db.Column(db.DateTime)
    
    def __init__(self, name, city, address, pin, phone_number, email, date_of_birth, member_since):
        self.name = name
        self.city = city
        self.address = address
        self.pin = pin
        self.phone_number = phone_number
        self.email = email
        self.date_of_birth = date_of_birth
        self.member_since = member_since

