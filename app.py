#--------------------------------------------------------Import Libraries------------------------------------------------------------------#
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")

from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta






#---------------------------------------------------Default objects creation----------------------------------------------------------------#
#region
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'

db = SQLAlchemy(app)
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = ph.hash("triggervarning")

@login_manager.user_loader
def load_user(user_id):
    # Check if the user is an admin
    admin = Admin.query.get(user_id)
    # If the user is not an admin, check if they are a regular member
    if admin is None:
        member = Members.query.get(user_id)
        # If the user is not a regular member, check if they are a trainer
        if member is None:
            trainer = Trainers.query.get(user_id)
            return trainer  # Return the trainer user if found
        return member  # Return the regular member user if found
    return admin  # Return the admin user if found
#endregion

#----------------------------------------------------------Classes--------------------------------------------------------------------------#
#region

class Session(db.Model):
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.String(10))
    trainer_comments = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

    def __init__(self,member_id):
        self.member_id = member_id
        self.start_time = datetime.now()
        db.session.add(self)
        db.session.commit()
    
    def close_session(member_id,trainer_comments):
        session = Session.query.filter_by(member_id=member_id,end_time=None)
        if session:
            session.end_time = datetime.now()
            time_duration = session.end_time - session.start_time
            session.duration = time_duration.seconds //60
            session.trainer_comments = trainer_comments
            db.session.commit()

class Package(db.Model):
    pkg_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    description = db.Column(db.String(100))
    price = db.Column(db.Integer)

    def __init__(self,name,duration,description,price):
        self.name = name
        self.duration = duration
        self.description = description
        self.price = price
        db.session.add(self)
        db.session.commit()
    
    def delete(id):
        del_pkg = Package.query.get(id)
        db.session.delete(del_pkg)
        db.session.commit()
    
    def modify(self,name,duration,description,price):
        self.name = name
        self.duration = duration
        self.description = description
        self.price = price
        db.session.commit()


class Subscription(db.Model):
    subscription_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    pkg_id = db.Column(db.Integer)
    mem_id = db.Column(db.String(10))
    completed = db.Column(db.Integer)





class Members(db.Model,UserMixin):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))  
    email = db.Column(db.String(100), nullable=False)
    member_since = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)
    trainer = db.Column(db.String(10))
    
    def __init__(self, name, phone_number, email, password, member_since):
        last_mem = Members.query.order_by(Members.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.member_since = member_since
        self.password = ph.hash(password)
        last_id=0
        if last_mem:
            last_id = int(last_mem.id[3:])
        self.id = f"mem{last_id+1}"

    def choose_trainer(self,trainer_id):
        self.trainer = trainer_id
        db.session.add(self)
        db.session.commit()

    def register(self):
        db.session.add(self)
        db.session.commit()

    

class Trainers(db.Model,UserMixin):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100))
    trainer_since = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone_number, email, password, experience, trainer_since):
        last_train = Trainers.query.order_by(Trainers.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.trainer_since = trainer_since
        self.experience = experience
        self.password = ph.hash(password)
        last_id=0
        if last_train:
            last_id = int(last_train.id[3:])
        self.id = f"tra{last_id+1}"

    def list_trainers():
        trainer_list = Trainers.query.all()
        return trainer_list

class Admin(db.Model,UserMixin):
    id   = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone_number, email, password):
        last_adm = Admin.query.order_by(Admin.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.password = ph.hash(password)
        last_id=0
        if last_adm:
            last_id = int(last_adm.id[3:])
        self.id  = f"adm{last_id+1}"

#endregion

#--------------------------------------------------------Routing Member----------------------------------------------------------------------#
#region
#home page
@app.route('/')
def homepage():
    return render_template('index.html', app_name='BulkBois', description='For the GymBros')

#Member registration
@app.route('/register', methods=["GET", "POST"])
def register():
    member = current_user
    if isinstance(member,Members):
        return redirect(url_for('dashboard'))
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
            member.register()
            return redirect(url_for("login"))
    
    return render_template("register.html",message_id=0)



#Member login
@app.route("/login", methods=["GET", "POST"])
def login():
    member = current_user
    if isinstance(member,Members):
        return redirect(url_for('dashboard'))
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
    member = current_user
    if isinstance(member,Members):
        return render_template("dashboard.html",member=member)
    return redirect(url_for("login"))   


#user logout
@app.route("/logout")
def logout():
    member = current_user
    if isinstance(member,Members):
        logout_user()
        return redirect(url_for("homepage"))
#endregion

#-------------------------------------------------------Routing Trainer----------------------------------------------------------------------#
#region
#trainer login
@app.route("/trainer/login", methods=["GET", "POST"])
def trainer_login():
    trainer = current_user
    if isinstance(trainer,Trainers):
        return redirect(url_for('trainer_dashboard'))
    if request.method == "POST":
        trainer = Trainers.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        try:
            if trainer and ph.verify(trainer.password, password):
                # The entered password matches the stored hashed password
                login_user(trainer)
                print("login")
                return redirect(url_for("trainer_dashboard"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Invalid email or password")
    return render_template("login.html")



# trainer dashboard
@app.route('/trainer/dashboard')
def trainer_dashboard():
    trainer = current_user
    if isinstance(trainer,Trainers):
        return trainer.email
    return redirect(url_for("trainer_login"))



#trainer logout
@app.route("/trainer/logout")
def trainer_logout():
    trainer = current_user
    if isinstance(trainer,Trainers):
        logout_user()
        return redirect(url_for("homepage"))

#endregion


#-------------------------------------------------------Routing Admin------------------------------------------------------------------------#
#region
#developement testing
@app.route('/temp')
def temp():
    all_records = Members.query.all()
    s=""
    for i,record in enumerate(all_records):
        s+=str(i)+str(record.__dict__)+'\n\t\t\t\t\t\t\t\t'
    return s

#create tables for db
@app.route('/admin/create_tables', methods=["POST","GET"])
def create_tables():
    if request.method == "POST":
        passwd = request.form.get("passwd")
        if ph.verify(app.config['SECRET_KEY'],passwd):
            with app.app_context():
                db.create_all()
            return 'Database tables created successfully!'
        else:
            return 'Wrong Password'
    return render_template('dev_tools.html',tool_id=0)


#create admin
@app.route('/admin/create_admin', methods=["POST","GET"])
def create_admin():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")
        dev_pass = request.form.get("dev_password")
        # Check if a user with the same email already exists
        existing_admin = Admin.query.filter_by(email=email).first()

        if existing_admin:
            return render_template("register.html",message_id=1)
        elif ph.verify(app.secret_key,dev_pass):

            # Create a new member
            admin = Admin(
                name=name,
                phone_number=phone_number,
                email=email,
                password=password,
            )

            db.session.add(admin)
            db.session.commit()
            return "created admin"
        else:
            return "error"
    return render_template('dev_tools.html',tool_id=1)



#Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    admin = current_user
    if isinstance(admin,Admin):
        return redirect(url_for('admin_panel'))
    if request.method == "POST":
        admin = Admin.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        try:
            if admin and ph.verify(admin.password, password):
                # The entered password matches the stored hashed password
                login_user(admin)
                print("login")
                return redirect(url_for("admin_panel"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Invalid email or password")
    return render_template("login.html")


# admin panel
@app.route('/admin/panel')
def admin_panel():
    admin = current_user
    if isinstance(admin,Admin):
        return render_template('admin/index.html',admin=admin)
    return redirect(url_for("admin_login"))

#hire trainer
@app.route('/admin/hire_trainer', methods=["GET","POST"])
def hire_trainer():
    admin = current_user
    if isinstance(admin,Admin):
        if request.method=="POST":
            name = request.form.get("name")
            phone_number = request.form.get("phone_number")
            experience = request.form.get("experience")
            email = request.form.get("email")
            passwd = request.form.get("password")
            trainer_since = datetime.now()

            existing_trainer = Trainers.query.filter_by(email=email).first()
            if existing_trainer:
                return render_template('/admin/hiretrainer.html', message_id=1,admin=admin)
            else:
                trainer = Trainers(
                    name = name,
                    phone_number = phone_number,
                    experience = experience,
                    email = email,
                    password = passwd,
                    trainer_since = trainer_since
                    )
                
                db.session.add(trainer)
                db.session.commit()
                return redirect(url_for('admin_panel'))
        return render_template('/admin/hiretrainer.html',admin=admin)
    return redirect(url_for('admin_login'))


@app.route("/admin/package")
def package_manager():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    package_list = Package.query.all()
    return render_template('/admin/package.html',admin=admin,pkgs=package_list)
    

@app.route("/admin/package/add", methods=["POST"])
def add_package():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        duration = int(request.form['duration'])
        description = request.form['description']
        price = int(request.form['price'])
        Package(name=name, duration=duration, description=description, price=price)
    return redirect(url_for('package_manager'))

@app.route("/admin/package/delete", methods=["POST"])
def delete_package():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    package_id = int(request.form.get('id'))
    Package.delete(package_id)
    return redirect(url_for('package_manager'))

@app.route("/admin/package/modify",methods=["GET","POST"])
def modify_package():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    id = request.args.get('id')
    package = Package.query.get(id)

    if request.method == 'POST':
        name = request.form.get('name')
        duration = request.form.get('duration')
        description = request.form.get('description')
        price = request.form.get('price')
        package.modify(name,duration,description,price)
        db.session.commit()

        return redirect(url_for('package_manager')) 

    return render_template("/admin/package_modify.html",admin=admin, package=package)

#admin logout
@app.route("/admin/logout")
def admin_logout():
    admin = current_user
    if isinstance(admin,Admin):
        logout_user()
        return redirect(url_for("homepage"))

#endregion

#---------------------------------------------------------------Run Flask--------------------------------------------------------------------#
if __name__ == '__main__':
    app.run()