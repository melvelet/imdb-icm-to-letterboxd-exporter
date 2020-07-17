import csv

import click


class ICMnIMDBtoLetterboxdImporter:
    def __init__(self):
        self.imdb_ratings = list()
        with open('ratings.csv', encoding='latin-1') as csvfile:
            imdb_ratings = csv.reader(csvfile, delimiter=',')
            for line in imdb_ratings:
                self.imdb_ratings.append(line)
        self.icm_checks = list()
        with open('checked.csv', encoding='latin-1') as csvfile:  # , encoding="unicode"
            icm_checks = csv.reader(csvfile, delimiter=',')
            for line in icm_checks:
                self.icm_checks.append(line)

    def initial_import(self):
        entries = dict()

        for row in self.imdb_ratings:
            if row[0] == 'Const':
                continue
            entries[row[0]] = {
                'rating': row[1],
                'date': row[2],
                'title': row[3]
            }

        for row in self.icm_checks:
            if 'imdburl' in row:
                continue
            imdb_id = row[8].split('/')[4]
            if imdb_id in entries:
                # print(entries[imdb]['date'], row[9], min(entries[imdb]['date'], row[9])[0:10])
                entries[imdb_id]['date'] = min(entries[imdb_id]['date'], row[9][0:10])
            else:
                entries[imdb_id] = {
                    'rating': None,
                    'date': row[9][0:10],
                    'title': row[0]
                }

        self.save_lines_to_csv(entries)

    def save_lines_to_csv(self, entries):
        header = ['imdbID', 'Title', 'WatchedDate', 'Rating10']
        lines = []
        for entry in entries:
            lines.append([entry, entries[entry]['title'], entries[entry]['date'], entries[entry]['rating']])

        for i in range((len(entries) // 1900) + 1):
            with open(f'results-{i+1}.csv', 'w') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(header)
                for line in lines[i*1900:(i+1)*1900]:
                    writer.writerow(line)

    def get_new_entries_since_date(self, date):
        entries = dict()
        for row in self.icm_checks:
            if 'imdburl' in row:
                continue
            entry_date = row[9][0:10]
            if entry_date >= date:
                imdb_id = row[8].split('/')[4]
                entries[imdb_id] = {
                    'rating': None,
                    'date': entry_date,
                    'title': row[0]
                }

        for row in self.imdb_ratings:
            if row[0] == 'Const':
                continue
            if row[0] in entries:
                entries[row[0]]['rating'] = row[1]

        self.save_lines_to_csv(entries)


@click.command()
@click.option("-d", "--start-date", type=str, required=False, help='Start date of imported logs')
def go(start_date):
    importer = ICMnIMDBtoLetterboxdImporter()
    if start_date:
        importer.get_new_entries_since_date(start_date)
    else:
        importer.initial_import()


if __name__ == '__main__':
    go()
