FROM ugodaniels/face-recognition

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]
