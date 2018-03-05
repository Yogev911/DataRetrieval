import api_handler


path = None
docname = None
author = None
cursor = api_handler.db.cnx.cursor()
query = ("SELECT docname,author,path FROM doc_tbl WHERE docid=%s")
data = (1,)
cursor.execute(query, data)
try:
    ret = cursor.fetchone()
    docname = ret[0]
    author = ret[1]
    path = ret[2]
except:
    pass
if path is not None:
    with open(path, 'r') as f:
        content = f.read()
else:
    content = 'Empty'
doc_data = {
    "docname": docname,
    "auther": author,
    "path": path,
    "content": content
}