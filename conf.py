import re
import traceback
local_db = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dataretrieval',
    'port': '3306'
}
remote_db = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dataretrieval',
    'port': '3306'
}

TEMPLATES = ['#Author name :',
             '#Year :',
             '#Intro :']

REGEX = re.compile('[^a-zA-Z \']')