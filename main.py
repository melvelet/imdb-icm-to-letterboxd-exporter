import csv
import requests
import click


class CSVDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.cookies_icm = {
            'PHPSESSID': "",
        }
        self.cookies_imdb = {
            "at-main": "",
            'ubid-main': "",
        }

    def get_icm_checks_csv(self):
        print("Downloading ICM checks...")
        icm_csv_url = "https://www.icheckmovies.com/movies/checked/?export"
        r = self.session.get(icm_csv_url, cookies=self.cookies_icm)
        with open(f'checked.csv', 'wb') as file:
            file.write(r.content)

    def get_imdb_ratings_csv(self):
        print("Downloading IMDb ratings...")
        imdb_csv_url = "https://www.imdb.com/user/ur13273039/ratings/export"
        r = self.session.get(imdb_csv_url, cookies=self.cookies_imdb)
        with open(f'ratings.csv', 'wb') as file:
            file.write(r.content)


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
            lines.insert(0, [entry, entries[entry]['title'], entries[entry]['date'], entries[entry]['rating']])

        for i in range((len(entries) // 1900) + 1):
            with open(f'results-{i+1}.csv', 'w', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(header)
                writer.writerows(lines[i*1900:(i+1)*1900])

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
    csv_dl = CSVDownloader()
    csv_dl.get_icm_checks_csv()
    csv_dl.get_imdb_ratings_csv()

    importer = ICMnIMDBtoLetterboxdImporter()
    if start_date:
        importer.get_new_entries_since_date(start_date)
    else:
        importer.initial_import()


if __name__ == '__main__':
    go()
