####Import modules
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_bcrypt import Bcrypt
from datetime import datetime 






####Default objects creation####
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config["SECRET_KEY"] = "HAHAIDK"

db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def loader_user(user_id):
    return Members.query.get(user_id)





####Classes####
class Members(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    address = db.Column(db.String(200))  
    pin = db.Column(db.String(10))
    phone_number = db.Column(db.String(15))  
    email = db.Column(db.String(100),nullable=False)
    date_of_birth = db.Column(db.Date)
    member_since = db.Column(db.DateTime)
    password = db.Column(db.String(60), nullable=False)
    
    def __init__(self, name="", city="", address="", pin="", phone_number="", email="", password="", date_of_birth="", member_since=""):
        self.name = name
        self.city = city
        self.address = address
        self.pin = pin
        self.phone_number = phone_number
        self.email = email
        self.date_of_birth = date_of_birth
        self.member_since = member_since
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')






####Routing####
@app.route('/')
def homepage():
    return render_template('index.html', app_name='BulkBois', description='For the GymBros')

@app.route('/temp')
def temp():
    all_records = Members.query.all()
    s=""
    for record in all_records:
        s+=str(record.__dict__)
    return s


@app.route('/create_tables')
def create_tables():
    return render_template('create_table.html')

@app.route('/table_created', methods = ["POST"])
def table_created():
    if request.method == "POST":
        passwd = request.form.get("passwd")
        if passwd==app.config['SECRET_KEY']:
            with app.app_context():
                db.create_all()
            return 'Database tables created successfully!'
        else:
            return 'Wrong Password'
    return render_template('create_table.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        city = request.form.get("city")
        address = request.form.get("address")
        pin = request.form.get("pin")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")

        # Convert date strings to date objects
        date_of_birth_str = request.form.get("date_of_birth")
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        
        # Set the "member_since" date to the current date
        member_since = datetime.now()

        # Create a new member
        member = Members(
            name=name,
            city=city,
            address=address,
            pin=pin,
            phone_number=phone_number,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
            member_since=member_since
        )

        db.session.add(member)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		member = Members.query.filter_by(
			username=request.form.get("username")).first()
		if member.password == request.form.get("password"):
			login_user(member)
			return redirect(url_for("dashboard"))
	return render_template("login.html")











if __name__ == '__main__':
    app.run()

























