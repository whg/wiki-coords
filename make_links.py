"""
Usage:
  make_links.py <language> [--dry-run] [--db=<db>]
  make_links.py (-h | --help)
  make_links.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --dry-run     Don't save to the database
  --db=<db>     Database to use [default: wiki_pages]
"""

import psycopg2
from psycopg2.extensions import AsIs
import re
from docopt import docopt
from util import make_title
from sys import stdout


def filepath(language, page):
    return 'geo_pages/%s/%s.wiki' % (language, page)


args = docopt(__doc__, version='0.1')
language = args['<language>']
dry_run = args['--dry-run']
db = psycopg2.connect("dbname=%s user=root" % args['--db'])
cursor = db.cursor()

links_re = re.compile(r'\[\[([^\]|]*)\]\]')

if not dry_run:
    table_name = '%s_links' % language
    cursor.execute('CREATE TABLE %s (id serial primary key, from_id bigint, to_id bigint)' % (table_name))
    db.commit()
    print('created table %s' % table_name)

cursor.execute('SELECT page, id FROM %s_pages' % (AsIs(language)))

pages = dict(cursor.fetchall())

print(len(pages))
added = 0
tried = 0
try:
    counter = 0
    for page, id in pages.items():
        with open(filepath(language, page)) as f:
            links = set(re.findall(links_re, f.read()))
            # print(len(links))
            # print(page)
            # print([make_title(link) for link in links[:5]])
            tried+= len(links)
            for link in links:
                link_title = make_title(link)
                if link_title in pages:
                    if not dry_run:
                        cursor.execute('INSERT INTO %s (from_id, to_id) VALUES (%s, %s)', (AsIs(table_name), id, pages[link_title]))
                    added+= 1
        counter+= 1

        if counter % 50 == 0:
            stdout.write('\r%d: added %d, tried %d' % (counter, added, tried))
except Exception as e:

    import traceback
    traceback.print_exc(file=stdout)
                   
finally:
    print('\nadded %d, tried %d' % (added,tried,))
    db.commit()
    cursor.close()
    db.close()

