import os
from dotenv import load_dotenv

load_dotenv()

# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///membership.db'

# New SQL DB
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.environ.get('SECRET_KEY')

# AWS Secrets
S3_BUCKET = os.environ["S3_BUCKET"]
S3_KEY = os.environ["S3_KEY"]
S3_SECRET = os.environ["S3_SECRET"]
# S3_LOCATION = f'http://{S3_BUCKET}.s3.amazonaws.com/'.format(S3_BUCKET)
