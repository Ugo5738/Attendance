# APP.PY MODULES
import os
import os.path
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from .forms import LoginForm, RegisterForm, AdminRegisterForm
# from .attendance import show_vid, attendance_db
# from filters import datetimeformat
from uuid import uuid1
import base64
import boto3
from dotenv import load_dotenv
from flask_debugtoolbar import DebugToolbarExtension

# FORM.PY MODULES
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (StringField, SubmitField, TextAreaField, PasswordField,
                     DateField, ValidationError, SelectField)
from wtforms.fields import TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import phonenumbers
import pycountry


# ATTENDANCE.PY MODULES
import cv2
import numpy as np
import face_recognition
import urllib.request as rq
# import os
from pathlib import Path
# from datetime import datetime
from calendar import Calendar
import csv


# FILTERS.PY MODULES
import arrow
import mimetypes


load_dotenv()


# FILTERS CONTENT
def datetimeformat(date_str):
    dt = arrow.get(date_str)
    return dt.humanize()


def file_type(key):
    file_info = os.path.splitext(key)
    file_extension = file_info[1]
    try:
        return mimetypes.types_map[file_extension]
    except KeyError():
        return "Unknown"


# ATTENDANCE CONTENT
base_path = Path(__file__).parent
path = os.path.join(base_path, "static")
path = os.path.join(path, "recog_images")

images = []
classNames = []
imageList = os.listdir(path)
# print(imageList)


Calendar = Calendar()
today = datetime.now()

YEAR = today.year
MONTH = today.month
FILE_NAME = 'Attendance.csv'

now = datetime.now()
time = now.strftime('%H:%M:%S')
date = now.strftime('%d-%B-%Y')
day = now.strftime('%A')
hour = now.strftime('%H')


for image_class in imageList:
    currentImg = cv2.imread(f"{path}/{image_class}")
    images.append(currentImg)
    classNames.append(os.path.splitext(image_class)[0])
# print(classNames)


def get_encodings(image_list):
    encode_list = []
    for ind, image in enumerate(image_list):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
    return encode_list


class MarkAttendance:
    def __init__(self, file_name, time_, date_, day_):
        self.file_name = file_name
        # self.person_name = person_name
        self.time = time_
        self.date = date_
        self.day = day_

    def exist_attendance(self, person_name):
        with open(self.file_name, 'r+') as file:
            name_list = []  # this could be put in a txt document
            content = file.readlines()
            header = content[:1]
            rows = content[1:]
            for entry in rows:
                entry = entry.split(", ")
                entry[-1] = entry[-1].split()[0]  # not sure that this line is needed
                full_name = f'{entry[0]} {entry[1]} {entry[2]}'
                name_list.append(full_name)
            if person_name not in name_list:
                new_member = person_name.split()
                first_name = new_member[0]
                middle_name = new_member[1]
                last_name = new_member[2]
                file.writelines(f"\n{first_name}, {middle_name}, {last_name}, {self.time}, {self.date}, {self.day}")

    def new_attendance(self, person_name):
        first_person = person_name.split()
        first_name = first_person[0]
        middle_name = first_person[1]
        last_name = first_person[2]
        attendance_file = open(self.file_name, 'w')
        attendance_file.write(f"First Name, Middle Name, Last Name, Time In, Date, Day")
        # mark attendance
        attendance_file.write(f"\n{first_name}, {middle_name}, {last_name}, {time}, {date}, {day}")
        attendance_file.close()

    def mark_present(self, person_name):
        if os.path.isfile(self.file_name):
            mark_attendance.exist_attendance(person_name=person_name)
        else:
            mark_attendance.new_attendance(person_name=person_name)


def attendance_db():
    with open('Attendance.csv') as file:
        content = file.readlines()
        header = content[:1]
        rows = content[1:]
        row_list = []
        for row in rows:
            row = row.split(", ")
            row[-1] = row[-1].split()[0]
            row_list.append(row)
        return row_list


mark_attendance = MarkAttendance(file_name=FILE_NAME, time_=time, date_=date, day_=day)

encode_list_for_known_faces = get_encodings(images)
# print("Encoding Complete")

# video_capture = cv2.VideoCapture(0)


def show_vid():
    CAM_START = False

    if day == os.environ.get("CHURCH_DAY", ""):
        if today.hour in range(int(os.environ.get("CHURCH_START_TIME", "")),
                               int(os.environ.get("CHURCH_STOP_TIME", ""))):
            CAM_START = True

    if CAM_START:
        url = [os.environ["CAM_URL"], os.environ.get("CAM_URL2", "")]

        while True:
            # capture frame by frame
            # success, img = video_capture.read()
            # if not success:
            #     break

            # if using the phone webcam
            img_resp = rq.urlopen(url[0])
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            img = cv2.imdecode(img_np, -1)
            print(img)

            # to resize output
            # width = int(cap.get(3))
            # height = int(cap.get(4))
            # cv2.resize(img, (0, 0), fx=0.5, fx=0.5)

            # resize frame for use
            img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
            # cv2.imshow('image_small', img_small)

            face_locations = face_recognition.face_locations(img_small)
            encoded_faces = face_recognition.face_encodings(img_small, face_locations)

            # for encodeFace, faceLoc in zip(encoded_faces, face_locations): # you can use an enumerate here
            for ind, (encodeFace, faceLoc) in enumerate(zip(encoded_faces, face_locations)):
                matches = face_recognition.compare_faces(encode_list_for_known_faces, encodeFace)
                name = "New member recognized"
                face_dist = face_recognition.face_distance(encode_list_for_known_faces, encodeFace)
                # print(face_dist)
                match_index = np.argmin(face_dist)
                print("match_index gotten", match_index)

                # display bounding box and name on image
                if matches[match_index]:
                    name = classNames[match_index].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                mark_attendance.mark_present(name)
                # else:
                #     mark_attendance(name)

            # cv2.imshow("video", img)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# FORM.PY CONTENTS
temp_country_dict = {}
for country in pycountry.countries:
    temp_country_dict[country.name] = country.alpha_2

country_dict = {}
for i in sorted(temp_country_dict):
    country_dict[i] = temp_country_dict[i]

countries = list(country_dict.keys())
COUNTRY_CHOICES = [("", "--Select an option--")]+[(country, country) for country in countries]
GENDER_CHOICES = [("", "--Select an option--"), ('Male', 'Male'), ('Female', 'Female')]
TITLE_CHOICES = [("", "--Select an option--"), ('Brother', 'Brother'), ('Sister', 'Sister'), ('Pastor', 'Pastor'),
                 ('Bible study', 'Bible study'), ('Teacher', 'Teacher'), ('Cell leader', 'Cell leader')]
BORN_AGAIN_CHOICES = [("", "--Select an option--"), ('1', 'Yes'), ('2', 'No')]
KNOW_US = [("", "--Select an option--"), ('1', 'Invited'), ('2', 'Social Media'), ('2', 'Television')]


# Create a Registration Form Class
class RegisterForm(FlaskForm):
    title = SelectField('Title:', validators=[DataRequired()], choices=TITLE_CHOICES)
    first_name = StringField("First name:", validators=[DataRequired()])
    middle_name = StringField("Middle name:", validators=[DataRequired()])
    last_name = StringField("Last name:", validators=[DataRequired()])
    address = TextAreaField("Address:", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    gender = SelectField("Gender:", validators=[DataRequired()], choices=GENDER_CHOICES)
    birth_date = DateField("Birth date", validators=[DataRequired()])
    phone = TelField('Phone: ', validators=[DataRequired()])
    country = SelectField('Country: ', validators=[DataRequired()], choices=COUNTRY_CHOICES)
    # others = TextAreaField('Others: ')
    submit = SubmitField("Submit")

    def validate_phone(self, phone):
        # phone_number = phone.data
        # if phone_number.startswith('0'):
        #     parse_num = phonenumbers.parse(phone_number, country_dict[self.coun.capitalize()])
        #     phone_number = phonenumbers.format_number(parse_num, phonenumbers.PhoneNumberFormat.E164)
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


# Create an Admin Registration Form Class
class AdminRegisterForm(FlaskForm):
    title = SelectField('Title:', validators=[DataRequired()], choices=TITLE_CHOICES)
    username = StringField("Username:", validators=[DataRequired()])
    first_name = StringField("First name:", validators=[DataRequired()])
    middle_name = StringField("Middle name:", validators=[DataRequired()])
    last_name = StringField("Last name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    role = StringField("Role:", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Login Form Class
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Cam Form Class
class CamForm(FlaskForm):
    ip = StringField('Ip:', validators=[DataRequired()])
    port = StringField("Port:")
    day = StringField("Day:")
    start_time = StringField("Start time:")
    stop_time = StringField("Stop time:", validators=[DataRequired()])
    submit = SubmitField("Turn On")


# Create access form
class AccessForm(FlaskForm):
    access_key = StringField("Access key:", validators=[DataRequired()])
    submit = SubmitField("Submit")


# APP.PY CONTENT
session = boto3.Session(
    aws_access_key_id=os.environ["S3_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET"]
)


app = Flask(__name__)
# Mobility(app)
app.config.from_pyfile('config.py')
# toolbar = DebugToolbarExtension(app)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

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
    ext = db.Column(db.String(100))
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


@app.route('/cam', methods=["GET", "POST"])
def cam():
    cam_form = CamForm()
    if request.method == "POST":
        if cam_form.validate_on_submit():
            ip = cam_form.ip.data
            port_ = cam_form.port.data
            day_ = cam_form.day.data
            start_time = cam_form.start_time.data
            stop_time = cam_form.stop_time.data
            if not port_:
                port_ = "8080"
            if not start_time:
                start_time = hour
            if not day_:
                day_ = day
            cam_url = f"http://{ip}:{port_}/shot.jpg"
            os.environ["CAM_URL"] = cam_url
            os.environ["CHURCH_DAY"] = day_
            os.environ["CHURCH_START_TIME"] = start_time
            os.environ["CHURCH_STOP_TIME"] = stop_time
            return redirect(url_for('index'))
    return render_template("cam.html", cam_form=cam_form)


@app.route('/files')
def files():
    s3_resource = session.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ["S3_BUCKET"])
    summaries = my_bucket.objects.all()
    return render_template("imageDB.html", my_bucket=my_bucket, files=summaries)


@app.route("/access", methods=["POST", "GET"])
def access():
    access_form = AccessForm()
    if request.method == 'POST':
        if access_form.validate_on_submit():
            if access_form.access_key.data == os.environ["ACCESS_KEY"]:
                return redirect(url_for("admin_register"))
    return render_template('access.html', access_form=access_form)


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


@app.route('/test', methods=['GET', 'POST'])
def test():
    member_form = RegisterForm()
    if request.method == 'POST':
        if member_form.validate_on_submit():
            return render_template("home.html")
        return render_template("registered.html")
    return render_template("register.html", member_form=member_form)


@app.route('/device', methods=['GET', 'POST'])
def device():
    return render_template('device.html')


@app.route('/mobile', methods=['Get', 'POST'])
def mobile():
    return render_template('mobile.html')


# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    member_form = RegisterForm()
    if request.method == 'POST':
        print("posting")
        if member_form.validate_on_submit():
            print("valid")
            email = member_form.email.data
            checked_email = Members.query.filter_by(email=email).first()
            first_name = member_form.first_name.data
            if checked_email is None:
                print("adding")
                reg_member = Members(title=member_form.title.data,
                                     first_name=member_form.first_name.data,
                                     middle_name=member_form.middle_name.data,
                                     last_name=member_form.last_name.data,
                                     address=member_form.address.data,
                                     email=member_form.email.data,
                                     gender=member_form.gender.data,
                                     birth_date=member_form.birth_date.data,
                                     phone=member_form.phone.data,
                                     country=member_form.country.data)
                db.session.add(reg_member)
                db.session.commit()
                email_id = Members.query.filter_by(email=email).first().id
                return redirect(url_for("upload", id=email_id))
            return render_template("registered.html", first_name=first_name)
    return render_template("register.html", member_form=member_form)


@app.route("/upload/<int:id>", methods=["GET", "POST"])
def upload(id):
    member_image_update = Members.query.get_or_404(id)
    if request.method == 'POST':
        file = request.files['file']
        ext = file.filename.split('.')[1]
        file_name = f"{member_image_update.first_name} {member_image_update.middle_name} {member_image_update.last_name}.{ext.lower()}"
        s3_resource = session.resource('s3')
        my_bucket = s3_resource.Bucket(os.environ["S3_BUCKET"])
        my_bucket.Object(file_name).put(Body=file)
        image_path = os.path.join(path, file_name)
        my_bucket.download_file(file_name, image_path)
        member_image_update.ext = ext.lower()
        db.session.commit()
        return render_template("uploaded.html", first_name=member_image_update.first_name)
    return render_template("upload.html", first_name=member_image_update.first_name)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    member_form = RegisterForm()
    member_to_update = Members.query.get_or_404(id)
    if request.method == "POST":
        if member_form.validate_on_submit():
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
            try:
                db.session.commit()
                return render_template("updated.html", first_name=member_to_update.first_name)
            except:
                return render_template("update.html", member_form=member_form, member_to_update=member_to_update)
    return render_template("update.html", member_form=member_form, member_to_update=member_to_update)


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
                # return redirect(url_for('dashboard'))
                return render_template("dashboard")
            else:
                flash("Wrong Password, Try Again")
        else:
            flash("That User doesn't exist, Try Again")
    return render_template("login.html", login_form=login_form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home'))


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
    file_name = f"{member_data.first_name} {member_data.middle_name} {member_data.last_name}.{member_data.ext}"
    image_dir = 'recog_images/'
    image_path = os.path.join(image_dir, file_name)
    return render_template("member.html", member_data=member_data, image_path=image_path)


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
