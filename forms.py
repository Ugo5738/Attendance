from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email


GENDER_CHOICES = [('1', 'Male'), ('2', 'Female')]
TITLE_CHOICES = [('1', 'Brother'), ('2', 'Sister'), ('1', 'Pastor')]
BORN_AGAIN_CHOICES = [('1', 'Yes'), ('2', 'No')]
KNOW_US = [('1', 'Invited'), ('2', 'Social Media'), ('2', 'Television')]


# Create a Registration Form Class
class RegisterForm(FlaskForm):
    first_name = StringField("First_name:", validators=[DataRequired()])
    middle_name = StringField("Middle_name:", validators=[DataRequired()])
    last_name = StringField("Last_name:", validators=[DataRequired()])
    address = TextAreaField("Address:", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    # image = FileField("Image", validators=[Email()])
    submit = SubmitField("Submit")

    # age = IntegerField("Age:", validators=[DataRequired()])
    # gender = SelectField("Gender:", choices=GENDER_CHOICES, validators=[DataRequired()])
    # phone = IntegerField("Phone:", validators=[DataRequired()])
    # birth_date = DateTimeField("Birth date", validators=[DataRequired()])
    # title = StringField("Title:", validators=[DataRequired()])
    # filename = FileField("Upload an Image of your face")
    # zip_code = IntegerField("Zip code:", validators=[DataRequired()])
    # city = StringField("City:", validators=[DataRequired()])
    # country = StringField("Country:", validators=[DataRequired()])
    # zone = StringField("Zone:", validators=[DataRequired()])
    # chapter = StringField("Chapter:", validators=[DataRequired()])
    # join_date = DateTimeField("When did you join Christ Embassy")
    # reason_for_joining = TextAreaField("Reason for joining:")
    # born_again = SelectField("Born Again:", choices=BORN_AGAIN_CHOICES, default=None)
    # how_did_you_find_us = StringField("How did you find us:", default=None)
    # attendance =
    # time =
