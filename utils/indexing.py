import glob
#Made By Yogev Heskia.
songs = []
path = 'doc*.txt'
files = glob.glob(path)
for file in files:
    songs.append(open(file, 'r').read().lower().split('\n\n'))
index_dict = {}
song_counter = 1
for song in songs:
    paragraph_counter = 1
    line_counter = 1
    for paragraph in song:
        line_counter = 1
        for line in paragraph.split('\n'):
            for word in line.split(' '):
                if word[-1:] == ',' or word[-1:] == ')' or word[-1:] == '(' or word[-1:] == '.': word = word[:-1]
                if word[:1] == ',' or word[:1] == ')' or word[:1] == '(' or word[:1] == '.': word = word[1:]
                if word not in index_dict:
                    index_dict[word] = 1
                else:
                    index_dict[word] += 1
            line_counter += 1
        paragraph_counter += 1
    song_counter += 1
index_text = open('index.txt', 'w')
for key in sorted(index_dict.iterkeys()): index_text.write("%s: %s" % (key,index_dict[key]) + '\n')