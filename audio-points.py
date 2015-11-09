"""
Usage:
  audio-points.py <data_file> [--output-dir=<d>] [--db=<db>]
  audio-points.py (-h | --help)
  audio-points.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --output-dir=<d>    Output file location [default: www]
  --db=<db>     Database to use [default: wiki]
"""
from docopt import docopt
import re
from os import path
import psycopg2
from psycopg2.extensions import AsIs
from sys import stdout

if __name__ == "__main__":

    args = docopt(__doc__, version='0.1')
    db = psycopg2.connect("dbname=%s user=root" % args['--db'])
    cursor = db.cursor()

    with open(args['<data_file>']) as f:
        lines = f.readlines()

    output = []
    for line in lines:
        
        wiki_name = path.basename(line.split('.wiki')[0])
#        wiki_name = file.replace('.wiki', '')
        
        oggs = re.findall('\|(?:audio=)?(?:\s*[a-zA-Z0-9_\-]+\s*=\s*)?([^\|:]+.ogg)', line)
        # if len(oggs) < 2: continue

        # print(wiki_name)
        # print(oggs)
        cursor.execute('SELECT id, lat, lon FROM en_pages WHERE page=%s', (wiki_name,))
        try:
            id, lat, lon = cursor.fetchone()
        except TypeError:
            print('fail on: %s' % line)
            continue

        for ogg in oggs:
            output.append((ogg, wiki_name, id, lat, lon))

    with open('sound_files.tsv', 'w') as f:
        for line in sorted(output, key=lambda e: e[2]):
            f.write('%s\n' % ('\t'.join([str(i) for i in line])))

    cursor.close()
    db.close()
