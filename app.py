from flask import Flask, render_template


app = Flask(__name__)


@app.route('/home')
def index():
    first_name = "James"
    return render_template("home.html", first_name=first_name)


@app.route('/member/<name>')
def member(name):
    return render_template("member.html", member_name=name)


# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

"""if __name__ == "__main__":
    app.run(debug=True)"""