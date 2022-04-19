from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (StringField, SubmitField, TextAreaField, PasswordField,
                     DateField, ValidationError, SelectField)
from wtforms.fields import TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField
import phonenumbers
import pycountry


COUNTRY_CHOICES = [("", "--Select an option--")]+[(country.name, country.name) for country in pycountry.countries]
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
    image = FileField("Image:", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


# Create an Admin Registration Form Class
class AdminRegisterForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired()])
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
