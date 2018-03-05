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


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yogev's page</title>
</head>
    <body>
        <form action="{{ url_for('search') }}" method="POST" enctype="multipart/form-data">
            <input type="text" name="query" value="" id="dd">
            <input type="submit" value="Search!" name="submit">
        </form>
    </body>
</html>