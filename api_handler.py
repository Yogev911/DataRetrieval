import mysql.connector
import traceback
import json
import ast
import re
import conf
import textract

# from dateutil.relativedelta import relativedelta

OK_MESSAGE = json.dumps({'msg': 'True'})
import os
import docx
import time, datetime

SAVE_PATH = 'uploads/'
STOP_LIST = set(['json', 'txt', 'xlsx'])
SPECIAL_CHARS = set(['.', ',', '(', ')', '(', '"'])


def create_res_obj(data, success=True):
    '''
    create return obj with array of data.
    :param data: dict of 'data_obj'
    :param success: json format for response
    :return:
    '''
    return json.dumps({
        "success": success,
        "data": data
    })


def data_obj(author, content, docname, path):
    '''
    create node of data object
    :param author: string
    :param content: string
    :param docname: string
    :param path: string
    :return: data_obj
    '''
    return {
        "docname": docname,
        "author": author,
        "path": path,
        "content": content
    }


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
            return create_res_obj({'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)},
                                  success=False)

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
                return create_res_obj({'traceback': traceback.format_exc(),
                                       'msg': "{} {}".format(e.message, e.args),
                                       'text': "DROP TABLE failed WITH TABLE {} ".format(str)},
                                      success=False)


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


def res_upload_file(file_name, path):
    try:
        global db
        db.connect()
        text = parse_file(path)
        print text
        values = parse_text_to_dict(text)
        # init_db()
        update_words_to_db(values['words_dict'], file_name, path, values['author'], values['year'], values['intro'])
        db.disconnect()
        return {'msg': 'got it!', 'filename': file_name, 'path': path, 'author': values['author'],
                'year': values['year'], 'intro': values['intro'], 'content': text}
    except Exception as e:
        return {'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)}


def get_file_extention(file_name):
    return str(file_name).split('.')[-1].lower()


def parse_file(file_path):
    if os.path.splitext(file_path)[1] == '.txt':
        return parse_text(file_path)
    else:
        return textract.process(file_path)


def index_text(text):
    regex = re.compile('[^a-zA-Z \']')
    text = regex.sub('', text)
    text = ' '.join(text.split())
    words_dict = {}
    for line in text.split('\n'):
        for word in line.split(' '):
            # if word[-1:] == ',' or word[-1:] == ')' or word[-1:] == '(' or word[-1:] == '.': word = word[:-1]
            if word[:1] == '\'': word = word[1:]
            # if word == '' or word == ' ':
            #     continue
            if word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1
    return words_dict


def parse_text_to_dict(text):
    author = 'None'
    year = 'None'
    intro = 'None'
    words_dict = {}
    for line in text.split('\n'):
        if line.startswith(conf.TEMPLATES[0]):
            author = line.replace(conf.TEMPLATES[0], '').strip()
        elif line.startswith(conf.TEMPLATES[1]):
            year = line.replace(conf.TEMPLATES[1], '').strip()
        elif line.startswith(conf.TEMPLATES[2]):
            intro = line.replace(conf.TEMPLATES[2], '').strip()
        else:
            tmp_line = conf.REGEX.sub('', line).lower()
            for word in tmp_line.split(' '):
                if word[:1] == '\'': word = word[1:]
                if word == '' or word == ' ':
                    continue
                if word not in words_dict:
                    words_dict[word] = 1
                else:
                    words_dict[word] += 1

    values = {'words_dict': words_dict,
              'author': author,
              'year': year,
              'intro': intro
              }
    return values


def parse_text(file_name):
    file = open(file_name, 'r')
    return file.read()
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


def update_words_to_db(words_dict, file_name, path, author, year, intro):
    if _is_duplicated_file(file_name):
        return 'file is already indexd'
    for key in sorted(words_dict.iterkeys()): _update_word(key, words_dict[key], file_name, path,
                                                           author, year, intro)
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


def _update_word(term, term_hits, file_name, path, author, year, intro):
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
            # found new term
            new_postid = _add_new_term(term)
            docid = _insert_row_doc_tbl(file_name, author, path, year, intro)
            _insert_row_postfile_tbl(new_postid, term_hits, docid)

        else:
            # found term which is alreay exists
            _inc_hit_indextbl(hit, postid)
            docid = _insert_row_doc_tbl(file_name, author, path, year, intro)
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


def _insert_row_doc_tbl(docname, author, path, year, intro):
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
        query = ("INSERT INTO doc_tbl (docname, author,path, year, intro) VALUES (%s , %s , %s, %s , %s)")
        data = (docname, author, path, year, intro)
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


def res_query(query):
    class MyTransformer(ast.NodeTransformer):
        def visit_Str(self, node):
            return ast.Set(words_dict[node.s])

    try:
        global db
        db.connect()
        data = []
        if not query.replace(')', '').replace('(', '').replace('AND', '').replace('OR', '').replace('NOT', '').replace(
                '"', '').strip():
            query = 'error'
        tmp_query = query.rstrip()
        if tmp_query.endswith(' AND') or tmp_query.endswith(' OR') or tmp_query.endswith(' NOT'):
            tmp_query = query.replace('AND', '').replace('OR', '').replace('NOT', '')
        string_with_quotes = ''
        if (not 'AND' in tmp_query) and (not 'OR' in tmp_query) and (not 'NOT' in tmp_query):
            query = ' '.join(tmp_query.split()).replace(' ', ' OR ')
        quotes_string = re.findall(r'"([^"]*)"', tmp_query)
        if len(quotes_string) == 1:
            query = query.replace("\"","")
        elif len(quotes_string) > 1:
            if quotes_string:
                string_with_quotes = ' '.join(tmp_query.split()).replace('AND', '').replace('OR', '').replace('NOT', '')
                for quote in quotes_string:
                    string_with_quotes = string_with_quotes.replace(quote, '')
                for quote in quotes_string:
                    string_with_quotes += ' OR (' + quote.replace(' ', ' AND ') + ')'
                string_with_quotes = string_with_quotes.replace('"', '').strip()
                if string_with_quotes.endswith('OR'):
                    string_with_quotes = string_with_quotes[:-3]
                if string_with_quotes.startswith('AND') or string_with_quotes.startswith('NOT'):
                    string_with_quotes = string_with_quotes[3:]
                if string_with_quotes.startswith('OR'):
                    string_with_quotes = string_with_quotes[2:]
                query = string_with_quotes

        tmp_query = query.replace(')', '').replace('(', '').replace('AND', '').replace('OR', '').replace('NOT', '')
        tmp_query = tmp_query.lower()
        words_list = tmp_query.split()

        words_list_in_quotes = ['\'' + re.sub("'","\\'", w) + '\'' for w in words_list]
        words_dict = {}
        for i in range(len(words_list)):
            words_dict[words_list[i]] = words_list_in_quotes[i]

        processed_query = ''
        for item in query.split():
            if item.lower() in words_dict:
                processed_query += words_dict[item.lower()]
            elif item.replace(')', '').lower() in words_dict:
                b = item.count(')')
                processed_query += words_dict[item.replace(')', '').lower()]
                processed_query += b * ')'
            elif item.replace('(', '').lower() in words_dict:
                b = item.count('(')
                processed_query += b * '('
                processed_query += words_dict[item.replace('(', '').lower()]
            else:
                processed_query += item
            processed_query += ' '
        for k, v in words_dict.iteritems():
            doc_list = get_doc_list_by_term(k)
            ast_list = create_ast_list(doc_list)
            words_dict[k] = ast_list

        processed_query = processed_query.replace('AND', '&')
        processed_query = processed_query.replace('OR', '|')
        processed_query = processed_query.replace('NOT', '-')

        input_code = ast.parse(processed_query, mode='eval')
        MyTransformer().visit(input_code)
        fixed = ast.fix_missing_locations(input_code)
        code = compile(fixed, '<string>', 'eval')
        result = eval(code)
        result = list(result)

        for doc_id in result:
            data.append(get_data_by_docid(doc_id, words_list))

        db.disconnect()
        return create_res_obj(data)
    except Exception as e:
        return create_res_obj({'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)},
                              success=False)


def create_ast_list(num_list):
    l = []
    if num_list is None:
        return l
    for num in num_list:
        l.append(ast.Num(num))
    return l


def get_doc_list_by_term(term):
    postid = None
    doc_list = []
    cursor = db.cnx.cursor()
    query = ("SELECT postid FROM indextable WHERE term=%s")
    data = (term,)
    cursor.execute(query, data)
    try:
        ret = cursor.fetchone()
        postid = ret[0]
    except:
        pass
    if postid is None:
        return doc_list
    query = ("SELECT docid FROM postfiletable WHERE postid=%s")
    data = (postid,)
    cursor.execute(query, data)
    try:
        for row in cursor:
            doc_list.append(row[0])
    except:
        pass
    return doc_list


def get_data_by_docid(doc_id, word_list):
    path = None
    docname = None
    author = None
    year = None
    intro = None
    cursor = db.cnx.cursor()
    query = ("SELECT docname,author,path,year,intro FROM doc_tbl WHERE docid =%s")
    data = (doc_id,)
    cursor.execute(query, data)
    try:
        ret = cursor.fetchone()
        docname = ret[0]
        author = ret[1]
        path = ret[2]
        year = ret[3]
        intro = ret[4]
    except:
        pass
    if path is not None:
        with open(path, 'r') as f:
            content = f.read()
    else:
        content = 'Empty'
    for term in word_list:
        content = re.sub(r'\b' + term + r'\b', '<b>'+term+'</b>', content,flags=re.IGNORECASE)
    doc_data = {
        "docname": docname,
        "auther": author,
        "path": path,
        "year": year,
        "intro": intro,
        "content": content
    }
    return doc_data


def delete_doc(docname):
    try:
        global db
        db.connect()
        cursor = db.cnx.cursor()
        postid_list = []
        query = ("SELECT path FROM doc_tbl WHERE docname=%s")
        data = (docname,)
        cursor.execute(query, data)
        doc_path = cursor.fetchone()[0]
        query = ("SELECT docid FROM doc_tbl WHERE path=%s")
        data = (doc_path,)
        cursor.execute(query, data)
        docid = cursor.fetchone()[0]
        query = ("SELECT postid FROM postfiletable WHERE docid=%s")
        data = (docid,)
        cursor.execute(query, data)
        for row in cursor:
            postid_list.append(row[0])
        for postid in postid_list:
            query = ("SELECT hit FROM indextable WHERE postid=%s")
            data = (postid,)
            cursor.execute(query, data)
            hit = cursor.fetchone()[0]
            if hit == 1:
                query = ("DELETE FROM indextable WHERE postid=%s")
                data = (postid,)
                cursor.execute(query, data)
                db.cnx.commit()
            else:
                new_hit = hit - 1
                query = ("UPDATE `indextable` SET `hit` = {} WHERE `indextable`.`postid` = %s").format(str(new_hit))
                data = (postid,)
                cursor.execute(query, data)
                db.cnx.commit()
        query = ("DELETE FROM postfiletable WHERE docid=%s")
        data = (docid,)
        cursor.execute(query, data)
        query = ("DELETE FROM doc_tbl WHERE docid=%s")
        data = (docid,)
        cursor.execute(query, data)
        if os.path.exists(doc_path):
            os.remove(doc_path)
        db.cnx.commit()
        db.disconnect()

        return create_res_obj(data)
    except Exception as e:
        return create_res_obj({'traceback': traceback.format_exc(), 'msg': "{} {}".format(e.message, e.args)},
                              success=False)
