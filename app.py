# APP.PY MODULES
import os
import os.path
import string
import secrets
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
# from .forms import LoginForm, RegisterForm, AdminRegisterForm
# from .attendance import show_vid, attendance_db
# from filters import datetimeformat
# from uuid import uuid1
import base64
import boto3
from threading import Timer
from dotenv import load_dotenv


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
path = os.path.join(path, "recogg_images")

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
                full_name = f'{entry[0]} {entry[1]} {entry[2]} {entry[3]}'
                name_list.append(full_name)
            if person_name.split('.')[0] not in name_list:
                new_member = person_name.split()
                first_name = new_member[0]
                middle_name = new_member[1]
                last_name = new_member[2]
                org_id = new_member[3].split('.')[0]
                file.writelines(f"\n{first_name}, {middle_name}, {last_name}, {org_id}, {self.time}, {self.date}, {self.day}")
            print(name_list)

    def new_attendance(self, person_name):
        first_person = person_name.split()
        first_name = first_person[0]
        middle_name = first_person[1]
        last_name = first_person[2]
        org_id = first_person[3].split('.')[0]
        attendance_file = open(self.file_name, 'w')
        attendance_file.write(f"First Name, Middle Name, Last Name, Organization id, Time In, Date, Day")
        # mark attendance
        attendance_file.write(f"\n{first_name}, {middle_name}, {last_name}, {org_id}, {time}, {date}, {day}")
        attendance_file.close()

    def mark_present(self, person_name):
        if os.path.isfile(self.file_name):
            mark_attendance.exist_attendance(person_name=person_name)
        else:
            mark_attendance.new_attendance(person_name=person_name)


def attendance_db(id_):
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


def delete_files(path, org_id):
    files = [file for file in os.listdir(path) if file.split('.')[0].split()[-1] == org_id]
    [os.remove(os.path.join(path, f)) for f in files]


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
ORGANIZATION_TYPE = [("", "--Select an option--"), ('Church', 'Church'), ('School', 'School'), ('Office', 'Office')]


class InstitutionForm(FlaskForm):
    institution_name = StringField("Institution name: ", validators=[DataRequired()])


# Create an Organization Form Class
class OrganizationRegisterForm(FlaskForm):
    org_name = StringField("Organization name:", validators=[DataRequired()])
    org_type = SelectField('Organization type:', validators=[DataRequired()], choices=ORGANIZATION_TYPE)
    org_username = StringField("Organization username:", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    password_hash = PasswordField('Password: ', validators=[DataRequired(),
                                                          EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


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
    org_name = StringField("Organization Name: ", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    org_token = StringField("Organization Token: ", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Cam Form Class
class CamForm(FlaskForm):
    ip = StringField('Ip:', validators=[DataRequired()])
    port = StringField("Port:")
    day = StringField("Day:")
    start_time = StringField("Start time:")
    stop_time = StringField("Stop time:", validators=[DataRequired()])
    token = StringField("Token:", validators=[DataRequired()])
    submit = SubmitField("Turn On")


# Create access form
class AccessForm(FlaskForm):
    access_token = StringField("Access Token:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AdLoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    password = StringField("Password: ", validators=[DataRequired()])
    admin_token = StringField("Access Token: ", validators=[DataRequired()])
    submit = SubmitField("Submit")


# APP.PY CONTENT
session = boto3.Session(
    aws_access_key_id=os.environ["S3_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET"]
)


app = Flask(__name__)
# Mobility(app)
app.config.from_pyfile('config.py')
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # 587 if using SSL
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = ('Daniel from Recogg', os.environ['MAIL_USERNAME'])
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(organization_id):
    return Organization.query.get(int(organization_id))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    middle_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    time_in = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    attendance_date = db.Column(db.DateTime, default=datetime.utcnow)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))


class Organization(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(400), nullable=False)
    org_type = db.Column(db.String(400), nullable=False)
    org_username = db.Column(db.String(400), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    org_token = db.Column(db.String(400), nullable=False, unique=True)
    ad_token = db.Column(db.String(400), nullable=False, unique=True)
    mem_token = db.Column(db.String(400), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    members = db.relationship('Member', backref='organization')
    admin_members = db.relationship('AdminMember', backref='organization')
    attendance = db.relationship('Attendance', backref='organization')
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Create String
    def __repr__(self):
        return "<Email %r>" % self.email

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# Create Model
class Member(db.Model):
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
    img_name = db.Column(db.Text, nullable=False)
    img = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

    # Create String
    def __repr__(self):
        return "<Email %r>" % self.email


class AdminMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    middle_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/ad_homepage')
def ad_homepage():
    return render_template("ad_homepage.html")


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/homepage/<token>')
def homepage(token):
    if Organization.query.filter_by(org_token=token).first():
        return render_template("org_homepage.html")
    # if token in for admin, render admin page
    elif Organization.query.filter_by(ad_token=token).first():
        ad_check = Organization.query.filter_by(ad_token=token).first()
        return render_template("ad_homepage.html", org_name=ad_check.org_name, token=token)


@app.route('/stream/<token>')
def index(token):
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(show_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cam/<token>', methods=["GET", "POST"])
def cam(token):
    cam_form = CamForm()
    if request.method == "POST":
        if cam_form.validate_on_submit():
            ip = cam_form.ip.data
            port_ = cam_form.port.data
            day_ = cam_form.day.data
            start_time = cam_form.start_time.data
            stop_time = cam_form.stop_time.data
            duration = (stop_time - start_time) * 3600
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
            if Organization.query.filter_by(org_token=token).first():
                org_id = Organization.query.filter_by(org_token=token).first().id
                org_members_set = Organization.query.filter_by(org_token=token).first().members
                img_name_list = [mem.img_name for mem in org_members_set]
                img_list = [mem.img for mem in org_members_set]
                img_dict = dict(zip(img_name_list, img_list))
                for img_name, img in img_dict.items():
                    file_path = os.path.join(path, img_name)
                    encoded_string = base64.b64encode(img)
                    with open(file_path, "wb") as new_file:
                        new_file.write(base64.decodebytes(encoded_string))
                t = Timer(duration, delete_files, [path, org_id])
                t.start()
                return redirect(url_for('index', token=token))
            elif Organization.query.filter_by(ad_token=token).first():
                org_id = Organization.query.filter_by(ad_token=token).first().id
                ad_members_set = Organization.query.filter_by(ad_token=token).first().members
                img_name_list = [mem.img_name for mem in ad_members_set]
                img_list = [mem.img for mem in ad_members_set]
                img_dict = dict(zip(img_name_list, img_list))
                for img_name, img in img_dict.items():
                    file_path = os.path.join(path, img_name)
                    encoded_string = base64.b64encode(img)
                    with open(file_path, "wb") as new_file:
                        new_file.write(base64.decodebytes(encoded_string))
                t = Timer(duration, delete_files, [path, org_id])
                t.start()
                return redirect(url_for('index', token=token))
    return render_template("cam.html", cam_form=cam_form)


@app.route('/attendance/<token>')
def attendance(token):
    # db.session.query(Attendance).delete()
    if Organization.query.filter_by(ad_token=token).first():
        org_id = Organization.query.filter_by(ad_token=token).first().id
        attendance_list = attendance_db(org_id)
        if attendance_list:
            for row in attendance_list:
                if org_id == row[3]:
                    member_attendance = Attendance(first_name=row[0],
                                                   middle_name=row[1],
                                                   last_name=row[2],
                                                   time_in=row[4],
                                                   date=row[5],
                                                   day=row[6],
                                                   organization_id=row[3])
                    db.session.add(member_attendance)
                    db.session.commit()
    if Organization.query.filter_by(org_token=token).first():
        org_id = current_user.id
        attendance_list = attendance_db(org_id)
        if attendance_list:
            for row in attendance_list:
                if org_id == row[3]:
                    member_attendance = Attendance(first_name=row[0],
                                                   middle_name=row[1],
                                                   last_name=row[2],
                                                   time_in=row[4],
                                                   date=row[5],
                                                   day=row[6],
                                                   organization_id=row[3])
                    db.session.add(member_attendance)
                    db.session.commit()
    signed_in_members = Attendance.query.order_by(Attendance.attendance_date)
    return render_template("attendance.html", signed_in_members=signed_in_members)


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
            token = access_form.access_token.data
            token_id = Organization.query.filter_by(ad_token=token).first().id
            if token_id:
                return redirect(url_for("attendance", token=token))
    return render_template('access.html', access_form=access_form)


# Organization Registration page
@app.route('/org_register', methods=['GET', 'POST'])
def org_register():
    org_form = OrganizationRegisterForm()
    if request.method == 'POST':
        if org_form.validate_on_submit():
            org_name = org_form.org_name.data
            org_username = org_form.org_username.data
            email = org_form.email.data
            checked_email = Organization.query.filter_by(email=email).first()
            if checked_email is None:
                # generate token
                alphabet = string.ascii_letters + string.digits
                while True:
                    org_token = ''.join(secrets.choice(alphabet) for i in range(15))
                    if (any(c.islower() for c in org_token)
                            and any(c.isupper() for c in org_token)
                            and sum(c.isdigit() for c in org_token) >= 3):
                        break
                while True:
                    ad_token = ''.join(secrets.choice(alphabet) for i in range(15))
                    if (any(c.islower() for c in ad_token)
                            and any(c.isupper() for c in ad_token)
                            and sum(c.isdigit() for c in ad_token) >= 3):
                        break
                while True:
                    mem_token = ''.join(secrets.choice(alphabet) for i in range(15))
                    if (any(c.islower() for c in mem_token)
                            and any(c.isupper() for c in mem_token)
                            and sum(c.isdigit() for c in mem_token) >= 3):
                        break
                # hash password
                hashed_pw = generate_password_hash(org_form.password_hash.data, "sha256")

                organization = Organization(org_name=org_form.org_name.data,
                                            org_type=org_form.org_type.data,
                                            org_username=org_form.org_username.data,
                                            email=org_form.email.data,
                                            org_token=org_token,
                                            ad_token=ad_token,
                                            mem_token=mem_token,
                                            password_hash=hashed_pw)
                db.session.add(organization)
                db.session.commit()

                mem_reg_url = url_for('register', mem_token=mem_token, _external=True)
                ad_reg_url = url_for('admin_register', ad_token=ad_token, _external=True)
                mail_body = f"Hi {org_name}," \
                            "<br><br>" \
                            "Welcome to Recogg, we are glad to have you on board." \
                            "<br><br>" \
                            "Here are your account credentials:" \
                            "<br>" \
                            f"Organization Name: {org_name}" \
                            "<br>" \
                            f"Organization Username: {org_username}" \
                            "<br>" \
                            f"Organization Email: {email}" \
                            "<br>" \
                            f"Access token: {org_token}" \
                            "<br><br>" \
                            "Admin registration<br>" \
                            "This gives admin access to certain individuals within your organization. We encouraged " \
                            "that it should be changed after first login.<br>" \
                            f"Access token: {ad_token}<br>" \
                            f"Admin Registration URL: {ad_reg_url}" \
                            "<br><br>" \
                            "Member registration<br>" \
                            "This link can be shared with members of your organization to fill in their details and " \
                            "upload an image of their face to enable Recogg recognise them. Please note that this " \
                            "only needs to be a one time process.<br>" \
                            f"{mem_reg_url}" \
                            "<br><br>" \
                            "However we understand that errors could be made during registration. Please use this " \
                            "update link to make modifications where necessary<br>" \
                            f"{'mem_update_url'}" \
                            "<br><br>" \
                            "Thanks,<br>" \
                            "Recogg Team"

                msg = Message('Registration Successful', recipients=[email])
                msg.html = mail_body
                mail.send(msg)

                logout_user()

                return render_template("org_success.html", org_name=org_name)
            return render_template("org_registered.html", org_name=org_name)
    return render_template('org_register.html', org_form=org_form)


# Login choice page
@app.route('/login_opt', methods=['GET', 'POST'])
def login_opt():
    return render_template('login_opt.html')


# Admin Login page
@app.route('/ad-login', methods=['GET', 'POST'])
def ad_login():
    ad_login_form = AdLoginForm()
    if request.method == 'POST':
        if ad_login_form.validate_on_submit():
            ad_token = ad_login_form.admin_token.data
            password = ad_login_form.password.data
            username = ad_login_form.username.data
            org_check = Organization.query.filter_by(ad_token=ad_token).first()
            if org_check:
                ad_members_set = org_check.admin_members
                if username in [ad.username for ad in ad_members_set]:
                    if True in [check_password_hash(ad.password_hash, password) for ad in ad_members_set]:
                        session['ad_username'] = username
                        return redirect(url_for('homepage', token=ad_token))
            # flash("Please input the correct details")
    return render_template('ad_login.html', ad_login_form=ad_login_form)


# Admin Registration page
@app.route('/admin_register/<ad_token>', methods=['GET', 'POST'])
def admin_register(ad_token):
    admin_form = AdminRegisterForm()
    if request.method == 'POST':
        if admin_form.validate_on_submit():
            organization_id = Organization.query.filter_by(ad_token=ad_token).first().id
            email = admin_form.email.data
            ad_members_set = Organization.query.filter_by(ad_token=ad_token).first().admin_members
            ad_list = [ad.email for ad in ad_members_set]
            if email not in ad_list:
                # hash password
                hashed_pw = generate_password_hash(admin_form.password_hash.data, "sha256")
                admin_member = AdminMember(title=admin_form.title.data,
                                           username=admin_form.username.data,
                                           first_name=admin_form.first_name.data,
                                           middle_name=admin_form.middle_name.data,
                                           last_name=admin_form.last_name.data,
                                           email=admin_form.email.data,
                                           role=admin_form.role.data,
                                           password_hash=hashed_pw,
                                           organization_id=organization_id)
                db.session.add(admin_member)
                db.session.commit()
                return render_template("success.html", first_name=admin_form.first_name.data)
    return render_template('admin_register.html', admin_form=admin_form)


# Registration page
@app.route('/register/<mem_token>', methods=['GET', 'POST'])
def register(mem_token):
    member_form = RegisterForm()
    if request.method == 'POST':
        if member_form.validate_on_submit():
            organization_id = Organization.query.filter_by(mem_token=mem_token).first().id
            members_set = Organization.query.filter_by(mem_token=mem_token).first().members
            mem_list = [ad.email for ad in members_set]
            email = member_form.email.data
            first_name = member_form.first_name.data
            middle_name = member_form.middle_name.data
            last_name = member_form.last_name.data
            pic = request.files['pic']
            ext = secure_filename(pic.filename).split('.')[-1]
            mimetype = pic.mimetype
            file_name = f"{first_name} {middle_name} {last_name} {organization_id}.{ext.lower()}"
            if email not in mem_list:
                reg_member = Member(title=member_form.title.data,
                                    first_name=member_form.first_name.data,
                                    middle_name=member_form.middle_name.data,
                                    last_name=member_form.last_name.data,
                                    address=member_form.address.data,
                                    email=member_form.email.data,
                                    gender=member_form.gender.data,
                                    birth_date=member_form.birth_date.data,
                                    phone=member_form.phone.data,
                                    country=member_form.country.data,
                                    img_name=file_name,
                                    img=pic.read(),
                                    mimetype=mimetype,
                                    organization_id=organization_id)
                db.session.add(reg_member)
                db.session.commit()
                return render_template("success.html", first_name=first_name)
            return render_template("registered.html", first_name=first_name)
    return render_template("register.html", member_form=member_form)


@app.route("/upload/<int:id>", methods=["GET", "POST"])
def upload(id):
    member_image_update = Member.query.get_or_404(id)
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
    member_to_update = Member.query.get_or_404(id)
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
    member_to_delete = Member.query.get_or_404(id)
    try:
        db.session.delete(member_to_delete)
        db.session.commit()
        all_members = Member.query.order_by(Member.registration_date)
        return render_template("database.html", all_members=all_members)
    except:
        flash("There was a problem deleting that record, please try again!")
        all_members = Member.query.order_by(Member.registration_date)
        return render_template("database.html", all_members=all_members)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        password = login_form.password_hash.data
        org_token = login_form.org_token.data
        org_check = Organization.query.filter_by(org_token=org_token).first()
        if org_check:
            if check_password_hash(org_check.password_hash, password):
                login_user(org_check)
                flash("Login Successful")
                return render_template("org_homepage.html", org_name=org_check.org_name)
            else:
                flash("Wrong Password, Try Again")
        else:
            flash("That User doesn't exist, Try Again")
    return render_template("org_login.html", login_form=login_form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home'))


@app.route("/dashboard/", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


def success():
    return render_template("success.html")


@app.route('/database/<token>')
def database(token):
    org_check = Organization.query.filter_by(org_token=token).first()
    ad_check = Organization.query.filter_by(ad_token=token).first()
    if org_check:
        organization_id = org_check.id
    elif ad_check:
        organization_id = ad_check.id
    else:
        organization_id = current_user.id
    all_members = Organization.query.filter_by(id=organization_id).first().members
    return render_template("database.html", all_members=all_members)


@app.route('/admin_database/<token>')
def admin_database(token):
    if Organization.query.filter_by(org_token=token).first():
        organization_id = Organization.query.filter_by(org_token=token).first().id
    elif Organization.query.filter_by(ad_token=token).first():
        organization_id = Organization.query.filter_by(ad_token=token).first().id
    else:
        organization_id = current_user.id
    all_admins = Organization.query.filter_by(id=organization_id).first().admin_members
    # admin_members = AdminMember.query.order_by(AdminMember.registration_date)
    return render_template("admin_data.html", admin_members=all_admins)


@app.route('/org_database')
def org_database():
    organizations = Organization.query.order_by(Organization.registration_date)
    return render_template("org_database.html", organizations=organizations)


@app.route('/delete_admin/<int:id>')
def delete_admin(id):
    admin_to_delete = AdminMember.query.get_or_404(id)
    try:
        db.session.delete(admin_to_delete)
        db.session.commit()
        admin_members = AdminMember.query.order_by(AdminMember.registration_date)
        return render_template("admin_data.html", admin_members=admin_members)
    except:
        flash("There was a problem deleting that record, please try again!")
        admin_members = Member.query.order_by(Member.registration_date)
        return render_template("admin_data.html", admin_members=admin_members)


@app.route('/member/<id>')
@login_required
def member(id):
    member_data = Member.query.get_or_404(id)
    file_name = f"{member_data.first_name} {member_data.middle_name} {member_data.last_name}.{member_data.ext}"
    # img = member_data.img
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
