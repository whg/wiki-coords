"""
Usage:
  redirect.py <wiki_file> [--seek=<b>] [--dry-run] [--db=<db>]
  redirect.py (-h | --help)
  redirect.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --seek=<b>    Seek to point in file [default: 0]
  --dry-run     Don't save to the database
  --db=<db>     Database to use [default: wiki_pages]
"""

import xml.etree.ElementTree as ET
from sys import stdout, argv
from glob import glob
import re
import psycopg2
from psycopg2.extensions import AsIs
import math
from docopt import docopt

from geotools import coordinate, wiki_coord, lat2y
from util import grab_partn, make_title, grab_parto


def lang_from_file(filename):
    
    matches = re.findall(r'([a-z]+)wiki', filename)
    if matches:
        return matches[0]

if __name__ == "__main__":
    args = docopt(__doc__, version='0.1')

    wikifile = args['<wiki_file>']
    language = lang_from_file(wikifile)


    
    db = psycopg2.connect("dbname=%s user=root" % args['--db'])
    cursor = db.cursor()
    f = open(wikifile)

    counter = 0
    added, failed = 0, 0
    buffer = ''


    if args['--seek']:
        f.seek(int(args['--seek']))
        print('seeked until %s' % args['--seek'])


    if not args['--dry-run']:
        try:
            cursor.execute('CREATE TABLE %s_redirects (id serial primary key, from_page text unique, to_id bigint)', (AsIs(language),))
            db.commit()
            print('created table %s_redirects' %(language))
        except psycopg2.ProgrammingError:
            print('tablealready exists')
    
    try:
        while True:
            try:
                payload, buffer = grab_partn(f, '<page>', '</page>', buffer)
            except EOFError:
                break
                

            counter+= 1    
            xml = ET.fromstring(payload)
                       
            redirect = xml.find('redirect')
            if redirect is not None:
                to_title = make_title(redirect.get('title'))
                from_title = make_title(xml.find('title').text)

                cursor.execute('SELECT id FROM %s_pages WHERE page=%s', (AsIs(language), to_title))
                to_id = cursor.fetchone()
                if not to_id:
                    failed+= 1
                    continue

                if not args['--dry-run']:
                    cursor.execute('INSERT INTO %s_redirects (from_page, to_id) VALUES (%s, %s)', (AsIs(language), from_title, to_id))
                added+= 1
    
                
            stdout.write('\r%d: added %d, failed %d' % (counter, added, failed))

    except Exception as e:
        print('\n\nfile at : ', f.tell())

        import traceback
        traceback.print_exc(file=stdout)
        # import IPython
        # IPython.embed()
    finally:
        print(counter)
    
        print('\nfile at : ', f.tell())
        f.close()
        db.commit()
        cursor.close()
        db.close()
