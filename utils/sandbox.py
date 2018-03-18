import conf
import re


def findWholeWord(w):
    return re.compile(r'\b{}\b'.format(w)).search


def is_in_order(arg1, arg2, list):
    any([arg1, arg2] == list[i:i + 2] for i in xrange(len(list) - 1))


operator = ['OR', 'AND', 'NOT']
data = []

query = 'hi two "two birds in the sky" my "hello\'"     name AND is OR (yogev   "heskia\'" dfk)   OR ("hiii" OR (bla OR boom)) NOT hi two "two" hello are'
query = query.replace("\'", "'")

# check for more than one operator in a row
splited_query = query.split()
duplicate_op_counter = 0
for first in operator:
    for second in operator:
        if not is_in_order(first, second, splited_query):
            duplicate_op_counter += 1
if duplicate_op_counter < 9:
    # bad query detet
    for op in operator:
        query = re.sub(r'\b' + op + r'\b', ' ', query)

tmp_quote = ''
quotes_string = re.findall(r'"([^"]*)"', query)
if quotes_string:
    for text in quotes_string:
        if len(text.split()) > 1:
            words_in_quotes = text.split()
            for item in words_in_quotes:
                tmp_quote += ' \"' + item + '\" '
            query = query.replace('\"{}\"'.format(text), tmp_quote, 1)
        tmp_quote = ''

# check for terms only without operators
tmp_query = re.sub(' +', ' ', query)
if tmp_query.endswith(' AND') or tmp_query.endswith(' OR') or tmp_query.endswith(' NOT'):
    tmp_query = query.replace('AND', '').replace('OR', '').replace('NOT', '')

if not query.replace(')', '').replace('(', '').replace('AND', '').replace('OR', '').replace('NOT', '').replace(
        '"', '').strip():
    query = 'error'

if not ((findWholeWord(operator[0])(query)) or (findWholeWord(operator[1])(query)) or (
        findWholeWord(operator[2])(query))):
    query = query.strip()
    query = ' OR '.join(query.split())

tmp_query = re.split(r'(OR|AND|NOT)', query)  # split to text OP text OP text

new_query = ''
for text in tmp_query:
    if text in operator:
        new_query += text + ' '
        continue
    if len(text.split()) > 1:
        new_query += '('
        for word in text.split():
            new_query += word + ' OR '
        new_query = new_query[:-3]
        new_query += ') '
    else:
        new_query += text

# remove stop list terms
query = new_query
quotes_words_indexs = []
for word in new_query.split():
    for term in conf.STOP_LIST:
        tmp_word = word.replace(')', '').replace('(', '').replace('"', '')
        if term == tmp_word:
            if word[0] == '\"' and word[-1] == '\"':
                quotes_words_indexs = [(m.start(0) + 1, m.end(0) - 2) for m in
                                       re.finditer(r'\b \"{}\" \b'.format(term), query)]
                if quotes_words_indexs:
                    # for uncover_word in quotes_words_indexs:
                    query = query[:quotes_words_indexs[0][0]] + ' ' + query[quotes_words_indexs[0][0] + 1:]
                    query = query[:quotes_words_indexs[0][1]] + ' ' + query[quotes_words_indexs[0][1] + 1:]
            else:
                quotes_words_indexs = [(m.start(0) + 1, m.end(0) - 2) for m in
                                       re.finditer(r'\b {} \b'.format(tmp_word), query)]
                # query = new_query.replace(tmp_word, 'STOPPED')
                query = query[:quotes_words_indexs[0][0]] + ' stoppedword ' + query[quotes_words_indexs[0][1] + 1:]
    quotes_words_indexs = []
query = re.sub(' +', ' ', query)

tmp_query = query.replace(')', '').replace('(', '').replace('AND', '').replace('OR', '').replace('NOT', '')
tmp_query = tmp_query.lower()
words_list = tmp_query.split()

words_list_in_quotes = ['\'' + re.sub("'", "\\'", w) + '\'' for w in words_list]
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
    if k in conf.STOP_LIST and k == 'stoppedword':
        ast_list = create_ast_list([])
    else:
        doc_list = get_doc_list_by_term(k, hidden_files)
        ast_list = create_ast_list(doc_list)
    words_dict[k] = ast_list

processed_query = processed_query.replace('AND', '&')
processed_query = processed_query.replace('OR', '|')
processed_query = processed_query.replace('NOT', '-')
