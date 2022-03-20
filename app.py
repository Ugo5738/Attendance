import os
import numpy as np
from flask import Flask, render_template, Response
from attendance import show_vid

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(show_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
