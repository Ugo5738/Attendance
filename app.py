import os.path

from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from forms import RegisterForm
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, IMAGES, UploadSet

from datetime import datetime

from attendance import show_vid, attendance_db


app = Flask(__name__)


# Old SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///membership.db'

# New SQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///root:passWord321@localhost/members'
app.config['SECRET_KEY'] = "super awesome! great to be working on this"
app.config['IMAGE_FOLDER'] = 'Images_upload/'
dab = SQLAlchemy(app)

# app.config['UPLOADED_IMAGES_DEST'] = 'Images_uploads/'
# images = UploadSet('images', IMAGES)
# configure_uploads(app, images)


class Attendance(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    first_name = dab.Column(dab.String(20), nullable=False)
    middle_name = dab.Column(dab.String(20), nullable=False)
    last_name = dab.Column(dab.String(20), nullable=False)
    time_in = dab.Column(dab.String(20), nullable=False)
    date = dab.Column(dab.String(20), nullable=False)
    day = dab.Column(dab.String(50), nullable=False)
    attendance_date = dab.Column(dab.DateTime, default=datetime.utcnow)


# Create Model
class Members(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    first_name = dab.Column(dab.String(20), nullable=False)
    middle_name = dab.Column(dab.String(20))
    last_name = dab.Column(dab.String(20), nullable=False)
    address = dab.Column(dab.String(20), nullable=False)
    email = dab.Column(dab.String(20), nullable=False, unique=True)
    filename = dab.Column(dab.String(50))
    data = dab.Column(dab.LargeBinary)
    registration_date = dab.Column(dab.DateTime, default=datetime.utcnow)

    # Create String
    def __repr__(self):
        return "<Email %r>" % self.email


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(show_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
                f = request.files['file']
                ext = f.filename.split('.')[1]
                file_name = f"{member_form.first_name.data} {member_form.middle_name.data} {member_form.last_name.data}.{ext.lower()}"
                # f_name = f"{member_form.first_name.data} {member_form.middle_name.data} {member_form.last_name.data}."
                # images.save(member_form.image.data, name=f_name)
                f.save(app.config['IMAGE_FOLDER'] + file_name)
                first_name = member_form.first_name.data
                member = Members(first_name=member_form.first_name.data,
                                 middle_name=member_form.middle_name.data,
                                 last_name=member_form.last_name.data,
                                 address=member_form.address.data,
                                 email=member_form.email.data,
                                 filename=f.filename,
                                 data=f.read())
                                 # image=member_form.image.data)
                dab.session.add(member)
                dab.session.commit()
                return render_template("success.html", first_name=first_name)
            return render_template("registered.html",
                                   first_name=first_name)
    return render_template("register.html",
                           member_form=member_form)


'''@app.route("/test", methods=['GET', 'POST'])
def test():
    member_form = RegisterForm()
    if member_form.validate_on_submit():
        full_name = f"{member_form.first_name.data} {member_form.middle_name.data} {member_form.last_name.data}."
        name = images.save(member_form.image.data)# , name=full_name)
        return f"File name: {name}"
    return render_template('test.html', member_form=member_form)'''


"""    # Validate Form
    print("I am here 1")
    if member_form.validate_on_submit():
        checked_email = Members.query.filter_by(email=member_form.email.data).first()
        print(checked_email)
        first_name = member_form.first_name.data
        if checked_email is None:
            member = Members(first_name=member_form.first_name.data,
                             middle_name=member_form.middle_name.data,
                             last_name=member_form.last_name.data,
                             address=member_form.address.data,
                             email=member_form.email.data,
                             # age=member_form.age.data,
                             # gender=member_form.gender.data,
                             # phone=member_form.phone.data,
                             # birth_date=member_form.birth_date.data,
                             # title=member_form.title.data,
                             # filename=member_form.filename.data,
                             # zip_code=member_form.zip_code.data,
                             # city=member_form.city.data,
                             # country=member_form.country.data,
                             # zone=member_form.zone.data,
                             # chapter=member_form.chapter.data,
                             # join_date=member_form.join_date.data,
                             # reason_for_joining=member_form.reason_for_joining.data,
                             # born_again=member_form.born_again.data,
                             # how_did_you_find_us=member_form.how_did_you_find_us.data
                             )
            db.session.add(member)
            db.session.commit()
            # member_form.data  # access all the form data
            # db login goes here
            print("\nData received. Now redirecting...")
            return render_template("success.html", first_name=first_name)
        return render_template("registered.html",
                               first_name=first_name)
    all_members = Members.query.order_by(Members.registration_date)
    print(all_members)
    return render_template("register.html",
                           member_form=member_form)
"""


def success():
    return render_template("success.html")


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/database')
def database():
    all_members = Members.query.order_by(Members.registration_date)
    return render_template("database.html", all_members=all_members)


@app.route('/attendance')
def attendance():
    dab.session.query(Attendance).delete()

    attendance_list = attendance_db()
    for row in attendance_list:
        member_attendance = Attendance(first_name=row[0],
                                       middle_name=row[1],
                                       last_name=row[2],
                                       time_in=row[3],
                                       date=row[4],
                                       day=row[5])
        dab.session.add(member_attendance)
        dab.session.commit()
    signed_in_members = Attendance.query.order_by(Attendance.attendance_date)
    return render_template("attendance.html", signed_in_members=signed_in_members)


@app.route('/member/<member_name>')
def member(member_name):
    return render_template("member.html", member_name=member_name)


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
