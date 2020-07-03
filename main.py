import csv



if __name__ == '__main__':
    entries = dict()
    with open('ratings.csv', encoding='latin-1') as csvfile:
        ratings = csv.reader(csvfile, delimiter=',')
        for row in ratings:
            if row[0] == 'Const':
                continue
            # print(row[0])
            entries[row[0]] = {
                'rating' : row[1],
                'date' : row[2],
                'title' : row[3]
            }
            # print(entries)
    with open('checked.csv', encoding='latin-1') as csvfile: #, encoding="unicode"
        checks = csv.reader(csvfile, delimiter=',')
        for row in checks:
            if 'imdburl' in row:
                continue
            imdb = row[8].split('/')[4]
            if imdb in entries:
                # print(entries[imdb]['date'], row[9], min(entries[imdb]['date'], row[9])[0:10])
                entries[imdb]['date'] = min(entries[imdb]['date'], row[9][0:10])
            else:
                entries[imdb] = {
                    'rating' : None,
                    'date' : row[9][0:10],
                    'title' : row[0]
                }
lines = [['imdbID', 'Title', 'WatchedDate', 'Rating10']]
for entry in entries:
    lines.append([entry, entries[entry]['title'], entries[entry]['date'], entries[entry]['rating']])

with open('results.csv','w') as file:
    writer = csv.writer(file, delimiter=',')
    for line in lines:
        writer.writerow(line)
