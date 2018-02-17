import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, request, jsonify , render_template


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def welcome():
    return 'Hello!,!'


@app.route('/index', methods=['GET', 'POST'])
def index():
    return '<h1>you are connected<h1>'

@app.route("/yogev",methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        return 'You are using POST'
    return render_template('index.html', output='hello')


if __name__ == '__main__':
    app.run()