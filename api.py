import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template, redirect, url_for
from api_handler import db_handler
import os
import time
import api_handler
import conf
import traceback
import threading
import threading

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = set(['dox', 'txt', 'docx'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def allowed_file(filename):
    return str(filename).split('.')[-1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def root():
    return 'hello! this is index!@#$'


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('upload.html')


@app.route('/init', methods=['GET', 'POST'])
def init():
    api_handler.init_db()
    return api_handler.create_res_obj([])


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        x = api_handler.res_query(query)
        x = jsonify(x)
        return x
    elif request.method == 'GET':
        return jsonify(api_handler.OK_MESSAGE)


@app.route('/delete/<filename>', methods=['GET', 'POST'])
def delete(filename):
    try:
        x = api_handler.delete_doc(filename)
        x = jsonify(x)
        return x
    except Exception as e:
        return api_handler.create_res_obj({'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)},
                      success=False)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'POST':
            files = ImmutableMultiDict([])
            return_data = []
            target = os.path.join(APP_ROOT, 'uploads')
            files = request.files.to_dict(flat=False)['file']

            for file in files:
                uuid = str(time.time()).split('.')[0]
                filename = uuid + secure_filename(file.filename)
                path = '/'.join([target, filename])
                file.save(path)
                filename = file.filename
                return_data.append(api_handler.res_upload_file(filename, path))

            errors_only =[]
            for data_block in return_data:
                if 'traceback' in data_block:
                    errors_only.append(data_block)
            if not errors_only:
                x = api_handler.create_res_obj(return_data)
            else:
                x = api_handler.create_res_obj(errors_only,success=False)
            return jsonify(x)
        elif request.method == 'GET':
            return redirect(url_for('admin'))
    except Exception as e:
        return jsonify(api_handler.create_res_obj({'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)},
                      success=False))


@app.route("/query", methods=['GET', 'POST'])
def yogev():
    if request.method == 'POST':
        query = request.form['query']
        return jsonify(api_handler.res_query(query))
    return jsonify(json.dumps({'msg': 'dude this is POST only!@'}))


if __name__ == '__main__':
    try:
        threading.Thread(target=api_handler.lisener,args=(conf.TMP_FOLDER,)).start()
    except:
        print traceback.format_exc()
    app.run()
