import mysql.connector
import traceback
import json
from dateutil.relativedelta import relativedelta
OK_MESSAGE = json.dumps({'msg': 'True'})
import os
import docx
import time,datetime
SAVE_PATH = 'uploads/'

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class db_handler(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.user = 'root'
        self.password = ''
        self.host = 'localhost',
        self.database = 'dataretrieval'
        self.port = 3306
        self.cnx = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               database=self.database,
                                               port=self.port)
        except Exception as e:
            print (traceback.format_exc())


    def disconnect(self):
        if self.cnx:
            self.cnx.close()

    #singelton
    @property
    def connection(self):
        if self.cnx is None:
            return self.connect()
        return self.cnx

    def get_all_tables(self):
        query = "SHOW TABLES"
        cursor = self.connection.cursor()
        cursor.execute(query)
        tables = cursor.fetchall()
        return tables

    def show_table(self,table_name):
        query = "SELECT * FROM " + table_name
        cursor = self.connection.cursor()
        cursor.execute(query)
        tables = []
        tables = cursor.fetchall()
        return tables

    def drop_all_tables(self):
        tables_names = []
        cursor = self.connection.cursor()
        tables_names = self.get_all_tables()
        for table_name in tables_names:
            str = ''.join(table_name)
            try:
                cursor.execute("drop table " + str)
            except Exception as e:
                print ("Drop table failed with table " + str + "   " + e.message + e.args)


def indexing(file_name):
    try:
        print 'testint'
        text = parse_file(file_name)
        print text
        dict = index_text(text)
        insert_words_to_db(dict)
        return OK_MESSAGE
    except Exception as e:
        print e.message
        print traceback.format_exc()
        return json.dumps({'msg': 'False', 'error': e.args, 'traceback': traceback.format_exc()})

def get_file_extention(file_name):
    return str(file_name).split('.')[-1].lower()


def parse_file(file_name):
    if get_file_extention(file_name) == 'txt':
        return parse_text(file_name)
    elif get_file_extention(file_name) == 'doc':
        return parse_doc(file_name)
    elif get_file_extention(file_name) == 'docx':
        return parse_docx(file_name)
    return OK_MESSAGE


def index_text(text):
    words_dict = {}
    for paragraph in text:
        for line in paragraph.split('\n'):
            for word in line.split(' '):
                if word[-1:] == ',' or word[-1:] == ')' or word[-1:] == '(' or word[-1:] == '.': word = word[:-1]
                if word[:1] == ',' or word[:1] == ')' or word[:1] == '(' or word[:1] == '.': word = word[1:]
                if word not in words_dict:
                    words_dict[word] = 1
                else:
                    words_dict[word] += 1
    return words_dict


def parse_text(file_name):
    with open(file_name, 'r').read().lower() as f:
        return f



def parse_doc(file_name):
    (fi, fo, fe) = os.popen3('catdoc -w "%s"' % file_name)
    fi.close()
    retval = fo.read()
    erroroutput = fe.read()
    fo.close()
    fe.close()
    if not erroroutput:
        return retval
    else:
        raise OSError("Executing the command caused an error: %s" % erroroutput)


def parse_docx(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        txt = para.text.encode('ascii', 'ignore')
        fullText.append(txt)
    return '\n'.join(fullText)


def insert_words_to_db(words_dict):
    # for key in sorted(words_dict.iterkeys()): THIS IS SQL QUERY FOR INSERT WORDS(key, words_dict[key]) #dict[word] = hits
    pass
    #




