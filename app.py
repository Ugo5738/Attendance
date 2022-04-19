import os
import os.path

from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .forms import LoginForm, RegisterForm, AdminRegisterForm
from .attendance import show_vid, attendance_db
from uuid import uuid1
import base64


app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(admin_id):
    return AdminMembers.query.get(int(admin_id))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    middle_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    time_in = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    attendance_date = db.Column(db.DateTime, default=datetime.utcnow)


# Create Model
class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(1024), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    gender = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    image_name = db.Column(db.String(100), nullable=False)
    image_data = db.Column(db.LargeBinary(), nullable=False)
    render_data = db.Column(db.Text(), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Create String
    def __repr__(self):
        return "<Email %r>" % self.email


class AdminMembers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    middle_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(show_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Admin Registration page
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    admin_form = AdminRegisterForm()
    if request.method == 'POST':
        if admin_form.validate_on_submit():
            # hash password
            hashed_pw = generate_password_hash(admin_form.password_hash.data, "sha256")
            admin_member = AdminMembers(title=admin_form.title.data,
                                        username=admin_form.username.data,
                                        first_name=admin_form.first_name.data,
                                        middle_name=admin_form.middle_name.data,
                                        last_name=admin_form.last_name.data,
                                        email=admin_form.email.data,
                                        role=admin_form.role.data,
                                        password_hash=hashed_pw)
            db.session.add(admin_member)
            db.session.commit()
        return render_template("success.html", first_name=admin_form.first_name.data)
    return render_template('admin_register.html', admin_form=admin_form)


# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    member_form = RegisterForm()
    if request.method == 'POST':
        if member_form.validate_on_submit():
            email = member_form.email.data
            checked_email = Members.query.filter_by(email=email).first()
            first_name = member_form.first_name.data
            if checked_email is None:
                file = request.files['image']
                image = file.read()
                render_image = base64.b64encode(image).decode('ascii')
                ext = file.filename.split('.')[1]
                file_name = f"{member_form.first_name.data} {member_form.middle_name.data} {member_form.last_name.data}.{ext.lower()}"
                secure_image = secure_filename(file_name)
                image_name = str(uuid1()) + "_" + secure_image
                file.save(app.config['IMAGE_FOLDER'] + file_name)
                first_name = member_form.first_name.data
                member = Members(title=member_form.title.data,
                                 first_name=member_form.first_name.data,
                                 middle_name=member_form.middle_name.data,
                                 last_name=member_form.last_name.data,
                                 address=member_form.address.data,
                                 email=member_form.email.data,
                                 gender=member_form.gender.data,
                                 birth_date=member_form.birth_date.data,
                                 phone=member_form.phone.data,
                                 country=member_form.country.data,
                                 image_data=image,
                                 image_name=image_name,
                                 render_data=render_image)
                db.session.add(member)
                db.session.commit()
                return render_template("success.html", first_name=first_name)
            return render_template("registered.html",
                                   first_name=first_name)
    return render_template("register.html",
                           member_form=member_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password_hash.data
        admin_username = AdminMembers.query.filter_by(username=username).first()
        if admin_username:
            if check_password_hash(admin_username.password_hash, password):
                login_user(admin_username)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password, Try Again")
        else:
            flash("That User doesn't exist, Try Again")
    return render_template('login.html',
                           login_form=login_form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


def success():
    return render_template("success.html")


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/database')
def database():
    all_members = Members.query.order_by(Members.registration_date)
    return render_template("database.html", all_members=all_members)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    member_form = RegisterForm()
    member_to_update = Members.query.get_or_404(id)
    if request.method == "POST":
        file = request.files['file']
        image = file.read()
        render_image = base64.b64encode(image).decode('ascii')
        ext = file.filename.split('.')[1]
        file_name = f"{member_form.first_name.data} {member_form.middle_name.data} {member_form.last_name.data}.{ext.lower()}"
        image_path = app.config['IMAGE_FOLDER'] + file_name
        secure_image = secure_filename(file_name)
        image_name = str(uuid1()) + "_" + secure_image
        if file_name in os.listdir(app.config['IMAGE_FOLDER']):
            os.remove(image_path)
        file.save(app.config['IMAGE_FOLDER'] + file_name)

        member_to_update.title = request.form['title']
        member_to_update.first_name = request.form['first_name']
        member_to_update.middle_name = request.form['middle_name']
        member_to_update.last_name = request.form['last_name']
        member_to_update.address = request.form['address']
        member_to_update.email = request.form['email']
        member_to_update.gender = request.form['gender']
        member_to_update.birth_date = request.form['birth_date']
        member_to_update.phone = request.form['phone']
        member_to_update.country = request.form['country']
        member_to_update.image_name = image_name
        member_to_update.image_data = image
        member_to_update.render_data = render_image
        try:
            db.session.commit()
            return render_template("updated.html",
                                   first_name=member_to_update.first_name)
        except:
            return render_template("update.html",
                                   member_form=member_form,
                                   member_to_update=member_to_update)
    else:
        return render_template("update.html",
                               member_form=member_form,
                               member_to_update=member_to_update)


@app.route('/delete/<int:id>')
def delete(id):
    member_to_delete = Members.query.get_or_404(id)
    try:
        db.session.delete(member_to_delete)
        db.session.commit()
        all_members = Members.query.order_by(Members.registration_date)
        return render_template("database.html", all_members=all_members)
    except:
        flash("There was a problem deleting that record, please try again!")
        all_members = Members.query.order_by(Members.registration_date)
        return render_template("database.html", all_members=all_members)


@app.route('/admin_database')
def admin_database():
    admin_members = AdminMembers.query.order_by(AdminMembers.registration_date)
    return render_template("admin_data.html", admin_members=admin_members)


@app.route('/delete_admin/<int:id>')
def delete_admin(id):
    admin_to_delete = AdminMembers.query.get_or_404(id)
    try:
        db.session.delete(admin_to_delete)
        db.session.commit()
        admin_members = AdminMembers.query.order_by(AdminMembers.registration_date)
        return render_template("admin_data.html", admin_members=admin_members)
    except:
        flash("There was a problem deleting that record, please try again!")
        admin_members = Members.query.order_by(Members.registration_date)
        return render_template("admin_data.html", admin_members=admin_members)


@app.route('/attendance')
def attendance():
    db.session.query(Attendance).delete()

    attendance_list = attendance_db()
    for row in attendance_list:
        member_attendance = Attendance(first_name=row[0],
                                       middle_name=row[1],
                                       last_name=row[2],
                                       time_in=row[3],
                                       date=row[4],
                                       day=row[5])
        db.session.add(member_attendance)
        db.session.commit()
    signed_in_members = Attendance.query.order_by(Attendance.attendance_date)
    return render_template("attendance.html", signed_in_members=signed_in_members)


@app.route('/member/<id>')
def member(id):
    member_data = Members.query.get_or_404(id)
    return render_template("member.html", member_data=member_data)


# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
