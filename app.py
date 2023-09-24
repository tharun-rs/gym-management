#--------------------------------------------------------Import Libraries------------------------------------------------------------------#
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime 






#---------------------------------------------------Default objects creation----------------------------------------------------------------#
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config["SECRET_KEY"] = "HAHAIDK"

db = SQLAlchemy(app)
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def loader_user(user_id):
    return Members.query.get(user_id)





#----------------------------------------------------------Classes--------------------------------------------------------------------------#
class Members(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))  
    email = db.Column(db.String(100),nullable=False)
    member_since = db.Column(db.DateTime)
    password = db.Column(db.String(60), nullable=False)
    
    def __init__(self, name, phone_number, email, password, member_since):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.member_since = member_since
        self.password = ph.hash(password)






#---------------------------------------------------------Routing---------------------------------------------------------------------------#
#home page
@app.route('/')
def homepage():
    return render_template('index.html', app_name='BulkBois', description='For the GymBros')

#developement testing
@app.route('/temp')
def temp():
    all_records = Members.query.all()
    s=""
    for i,record in enumerate(all_records):
        s+=str(i)+str(record.__dict__)+'\n\t\t\t\t\t\t\t\t'
    return s

#create tables for db
@app.route('/create_tables', methods=["POST","GET"])
def create_tables():
    if request.method == "POST":
        passwd = request.form.get("passwd")
        if passwd==app.config['SECRET_KEY']:
            with app.app_context():
                db.create_all()
            return 'Database tables created successfully!'
        else:
            return 'Wrong Password'
    return render_template('create_table.html')


#Member registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")
        # Check if a user with the same email already exists
        existing_member = Members.query.filter_by(email=email).first()

        if existing_member:
            return render_template("register.html",message_id=1)
        else:
            # Set the "member_since" date to the current date
            member_since = datetime.now()

            # Create a new member
            member = Members(
                name=name,
                phone_number=phone_number,
                email=email,
                password=password,
                member_since=member_since
            )

            db.session.add(member)
            db.session.commit()
            return redirect(url_for("login"))
    
    return render_template("register.html",message_id=0)



#Member login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        member = Members.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        try:
            if member and ph.verify(member.password, password):
                # The entered password matches the stored hashed password
                login_user(member)
                print("login")
                return redirect(url_for("dashboard"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Invalid email or password")


    return render_template("login.html")

#user dashboard
@app.route("/dashboard")
def dashboard():
     try:
        member = current_user
        return member.email
     except Exception:
         return "Not Logged in"


#user logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))





#---------------------------------------------------------------Run Flask-------------------------------------------------------------------#
if __name__ == '__main__':
    app.run()

























