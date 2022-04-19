import os
from dotenv import load_dotenv

load_dotenv()

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///membership.db'

# New SQL DB
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.environ.get('SECRET_KEY')
IMAGE_FOLDER = os.environ.get('IMAGE_FOLDER', 'Images_upload/')

# AWS Secrets
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_KEY_ID = os.environ.get('AWS_KEY_ID')
