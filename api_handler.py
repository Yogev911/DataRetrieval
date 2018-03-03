import mysql.connector
import traceback
import json
# from dateutil.relativedelta import relativedelta

OK_MESSAGE = json.dumps({'msg': 'True'})
import os
import docx
import time, datetime

SAVE_PATH = 'uploads/'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class db_handler(object):
    # __metaclass__ = Singleton

    def __init__(self):
        self.user = 'root'
        self.password = ''
        self.host = 'localhost'
        self.database = 'dataretrieval'
        self.port = '3306'
        self.cnx = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               database=self.database,
                                               port=self.port)

        except Exception as e:
            print traceback.format_exc()

    def disconnect(self):
        if self.cnx:
            self.cnx.close()

    # singelton
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

    def show_table(self, table_name):
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
                print ("DROP TABLE failed WITH TABLE " + str + "   " + e.message + e.args)


def testing():
    db = db_handler()
    db.connect()
    _update_word('yogev', 11, 'dfgfg')
    # cursor = db.cnx.cursor()
    # query = ("insert into Indextable (term, hit) VALUES ('bla' , 567)")
    # cursor.execute(query)
    # query = ("insert into Indextable (term, hit) VALUES ('sss' , 345)")
    # cursor.execute(query)
    # query = ("insert into Indextable (term, hit) VALUES ('rrr' , 657)")
    # cursor.execute(query)
    # id = cursor.lastrowid
    # db.cnx.commit()
    # query = "SELECT `postid` FROM `Indextable` WHERE `term` = 'tt'"
    # query = ("SELECT postid,hit FROM Indextable WHERE term=%s")
    # data = ('rrr',)
    # cursor.execute(query, data)
    # if cursor:
    #     ret = cursor.fetchone()
    #     i ret:`
    #         print ret[0]

    query = ("SELECT postid,hit FROM Indextable WHERE term=%s")
    data = ('sss',)
    cursor.execute(query, data)
    ret = cursor.fetchone()
    postid = ret[0]
    hit = ret[0]
    db.disconnect()
    print 'fffff'


db = db_handler()


def init_db():
    global db
    db.connect()
    cursor = db.cnx.cursor()
    query = "DELETE FROM `indextable`"
    cursor.execute(query)
    db.cnx.commit()
    query = "DELETE FROM `doc_tbl`"
    cursor.execute(query)
    db.cnx.commit()
    query = "DELETE FROM `postfiletable`"
    cursor.execute(query)
    db.cnx.commit()
    query = "ALTER TABLE indextable AUTO_INCREMENT = 1"
    cursor.execute(query)
    db.cnx.commit()
    query = "ALTER TABLE doc_tbl AUTO_INCREMENT = 1"
    cursor.execute(query)
    db.cnx.commit()
    query = "ALTER TABLE postfiletable AUTO_INCREMENT = 1"
    cursor.execute(query)
    db.cnx.commit()




def indexing(file_name,path):
    try:
        global db
        db.connect()
        text = parse_file(path)
        print text
        dict = index_text(text)
        # init_db()
        update_words_to_db(dict, file_name,path)
        db.disconnect()
        return OK_MESSAGE
    except Exception as e:
        print e.message
        print traceback.format_exc()
        return json.dumps({'msg': 'False', 'error': e.args, 'traceback': traceback.format_exc()})


def get_file_extention(file_name):
    return str(file_name).split('.')[-1].lower()


def parse_file(file_path):
    if get_file_extention(file_path) == 'txt':
        return parse_text(file_path)
    elif get_file_extention(file_path) == 'doc':
        return parse_doc(file_path)
    elif get_file_extention(file_path) == 'docx':
        return parse_docx(file_path)
    return OK_MESSAGE


def index_text(text):
    words_dict = {}
    for line in text.split('\n'):
        for word in line.split(' '):
            if word[-1:] == ',' or word[-1:] == ')' or word[-1:] == '(' or word[-1:] == '.': word = word[:-1]
            if word[:1] == ',' or word[:1] == ')' or word[:1] == '(' or word[:1] == '.': word = word[1:]
            if word == '' or word == ' ':
                continue
            if word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1
    return words_dict


def parse_text(file_name):
    file = open(file_name, 'r')
    return file.read().lower()
    # with open(file_name, 'r').read().lower() as f:
    #     return f


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


def update_words_to_db(words_dict, file_name,path):
    for key in sorted(words_dict.iterkeys()): _update_word(key, words_dict[key], file_name, path)  # dict[word] = hits
    pass


def _is_duplicated_file(docname):
    docid = None
    cursor = db.cnx.cursor()
    query = ("SELECT docid FROM doc_tbl WHERE docname=%s")
    data = (docname,)
    cursor.execute(query, data)
    try:
        ret = cursor.fetchone()
        docid = ret[0]
    except:
        pass
    if docid:
        return True
    return False


def _update_word(term, term_hits, file_name , path):
    try:
        cursor = db.cnx.cursor()
        query = ("SELECT postid,hit FROM Indextable WHERE term=%s")
        data = (term,)
        cursor.execute(query, data)
        try:
            ret = cursor.fetchone()
            postid = ret[0]
            hit = ret[1]
        except:
            pass
        if not ret:
            new_postid = _add_new_term(term)
            docid = _insert_row_doc_tbl(file_name, 'authorr', path)
            _insert_row_postfile_tbl(new_postid, term_hits, docid)

        else:
            if _is_duplicated_file(file_name):
                print 'file is already indexd'
            else:
                _inc_hit_indextbl(hit, postid)
                docid = _insert_row_doc_tbl(file_name, 'authorr', path)
                _insert_row_postfile_tbl(postid, term_hits, docid)
        cursor.close()
        return True
    except:
        print traceback.format_exc()
        return False


def _add_new_term(term):
    '''
    :param term: add new row with term, hit = 1
    :return: the new postfile id
    '''
    cursor = db.cnx.cursor()
    query = ("INSERT INTO Indextable (term, hit) VALUES (%s , 1)")
    data = (term,)
    cursor.execute(query, data)
    new_postfile_id = cursor.lastrowid
    db.cnx.commit()
    try:
        query = ("SELECT postid FROM Indextable WHERE term=%s")
        data = (term,)
        cursor.execute(query, data)
        new_postfile_id = cursor.fetchone()[0]
    except:
        pass
    db.cnx.commit()
    cursor.close()
    return new_postfile_id


def _inc_hit_indextbl(old_hit, postid):
    '''
    :param old_hit: number of doc hits
    :param postid: postid to update
    :return: bool
    '''
    cursor = db.cnx.cursor()
    new_hit = old_hit + 1
    query = ("UPDATE `indextable` SET `hit` = {} WHERE `indextable`.`postid` = %s").format(str(new_hit))
    data = (postid,)
    cursor.execute(query, data)
    db.cnx.commit()
    cursor.close()
    return True


def _insert_row_postfile_tbl(postid, term_hits, docid):
    cursor = db.cnx.cursor()
    query = ("INSERT INTO postfiletable (postid, hit, docid) VALUES (%s , %s , %s)")
    data = (postid, term_hits, docid)
    cursor.execute(query, data)
    db.cnx.commit()
    cursor.close()
    return True


def _insert_row_doc_tbl(docname, author, path):
    '''
    :param docname:
    :param author:
    :param path:
    :return: id of the row
    '''
    docid = None
    cursor = db.cnx.cursor()
    query = ("SELECT docid FROM doc_tbl WHERE path=%s")
    data = (path,)
    cursor.execute(query, data)
    try:
        ret = cursor.fetchone()
        docid = ret[0]
    except:
        pass

    if docid:
        return docid
    else:
        query = ("INSERT INTO doc_tbl (docname, author,path) VALUES (%s , %s , %s)")
        data = (docname, author, path)
        cursor.execute(query, data)
        db.cnx.commit()
        query = ("SELECT docid FROM doc_tbl WHERE path=%s")
        data = (path,)
        cursor.execute(query, data)
        try:
            docid = cursor.fetchone()[0]
        except:
            pass
        db.cnx.commit()
        cursor.close()
        return docid
