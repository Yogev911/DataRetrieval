import re
import conf
path = '/Users/yogev/Documents/DataRetrieval/static/THE BATTLE OF NEW ORLEANS.txt'



with open(path) as f:
    text = f.read()

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
        tmp_line = conf.REGEX.sub('', line)
        for word in tmp_line.split(' '):
            if word[:1] == '\'': word = word[1:]
            if word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1

