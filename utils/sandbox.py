import conf
import re

operator = ['OR', 'AND', 'NOT']
data = []
query = 'sdfbsdfbdf'


def findWholeWord(w):
    return re.compile(r'\b' + w + '\b').search


# remove stop list terms
for term in conf.STOP_LIST:
    query = re.sub(r'\b' + term + r'\b', ' ', query,flags=re.IGNORECASE)


def is_in_order(arg1, arg2, list):
    any([arg1, arg2] == list[i:i + 2] for i in xrange(len(list) - 1))


# check for terms only without operators
if not (findWholeWord(operator[0])(query)) or (findWholeWord(operator[1])(query)) or (findWholeWord(operator[2])(query)):
    query = query.strip()
    query = ' OR '.join(query.split())
else:
    # check for more than one operator in a row
    splited_query = query.split()
    duplicate_op_counter = 0
    for first in operator:
        for second in operator:
            if not is_in_order(first, second, splited_query):
                duplicate_op_counter+=1
    if duplicate_op_counter < 9:
        # bad query detet
        for op in operator:
            query = re.sub(r'\b'+op+r'\b', ' ', query)

    else:
        pass




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
    query = query.replace("\"", "")
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
    doc_list = get_doc_list_by_term(k)
    ast_list = create_ast_list(doc_list)
    words_dict[k] = ast_list

processed_query = processed_query.replace('AND', '&')
processed_query = processed_query.replace('OR', '|')
processed_query = processed_query.replace('NOT', '-')
