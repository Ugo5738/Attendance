FROM ugodaniels/face-recognition

COPY . /app
WORKDIR /app

CMD ["python3", "app.py"]
