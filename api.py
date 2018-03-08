import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template, redirect, url_for
from api_handler import db_handler
import os
import time
import api_handler

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
    return 'index'


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        x = api_handler.res_query(query)
        x = jsonify(x)
        return x
    elif request.method == 'GET':
        return render_template('index.html')


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        path = request.form['del_path']
        x = api_handler.delete_doc(path)
        x = jsonify(x)
        return x
    elif request.method == 'GET':
        return render_template('delete.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        return_data = []
        target = os.path.join(APP_ROOT, 'uploads')
        author = request.form['author']
        files = request.files.getlist('file')
        for file in files:
            uuid = str(time.time()).split('.')[0]
            filename = uuid + secure_filename(file.filename)
            path = '/'.join([target, filename])
            file.save(path)
            filename = file.filename
            return_data.append(api_handler.res_upload_file(filename, path, author))
        return api_handler.create_res_obj(return_data)
    elif request.method == 'GET':
        return redirect(url_for('admin'))



@app.route("/query", methods=['GET', 'POST'])
def yogev():
    if request.method == 'POST':
        query = request.form['query']
        return jsonify(api_handler.res_query(query))
    return jsonify(json.dumps({'msg': 'dude this is POST only!@'}))


if __name__ == '__main__':
    app.run()
