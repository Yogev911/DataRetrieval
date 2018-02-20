import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, request, jsonify , render_template
from api_handler import db_handler


app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = set(['json', 'txt', 'xlsx'])

def allowed_file(filename):
    # this has changed from the original example because the original did not work for me
    return str(filename).split('.')[-1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/upload', methods=['GET', 'POST'])
def set_json():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        if allowed_file(filename):
            return jsonify(parse_util.update_json_in_db(file))
        return jsonify(json.dumps({'msg': 'are you trying to fuck up my server? send me only json/xls/xlsx files!'}))
    else:
        return jsonify(json.dumps({'msg': 'dude this is POST only!@'}))

if __name__ == '__main__':
    app.run()