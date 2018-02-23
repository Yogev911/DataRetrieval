import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, request, jsonify , render_template
from api_handler import db_handler
import os
import time
import api_handler


app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = set(['json', 'txt', 'xlsx'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def allowed_file(filename):
    # this has changed from the original example because the original did not work for me
    return str(filename).split('.')[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('upload.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    return 'index'

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    target = os.path.join(APP_ROOT,'uploads')
    print target
    file = request.files['file']
    print file
    uuid = str(time.time()).split('.')[0]
    filename = uuid + secure_filename(file.filename)
    dest = '/'.join([target,filename])
    print dest
    file.save(dest)
    time.sleep(5)
    # api_handler.indexing(dest)

    print 'l,l,l,kmk'
    api_handler.indexing(filename)
    return render_template('upload.html', table = 'table')

@app.route("/yogev",methods=['GET', 'POST'])
def yogev():
    return render_template('upload.html')

# @app.route('/upload', methods=['GET', 'POST'])
# def set_json():
#     if request.method == 'POST':
#         file = request.files['file']
#         filename = file.filename
#         if allowed_file(filename):
#             return jsonify(parse_util.update_json_in_db(file))
#         return jsonify(json.dumps({'msg': 'are you trying to fuck up my server? send me only json/xls/xlsx files!'}))
#     else:
#         return jsonify(json.dumps({'msg': 'dude this is POST only!@'}))

if __name__ == '__main__':
    app.run()