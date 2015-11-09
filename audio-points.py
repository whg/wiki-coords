"""
Usage:
  audio-points.py <data_file> [--output-dir=<d>] [--db=<db>]
  audio-points.py (-h | --help)
  audio-points.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --output-dir=<d>    Output file location [default: www]
  --db=<db>     Database to use [default: en_wiki]
"""
from docopt import docopt
import re
from os import path
from sys import stdout
import mysql.connector as mysql
from mysql.connector import errors
from collections import defaultdict

if __name__ == "__main__":

    args = docopt(__doc__, version='0.1')
    db = mysql.connect(host="localhost", user="root", passwd="", db=args['--db'])
    cursor = db.cursor()

    with open(args['<data_file>']) as f:
        lines = f.readlines()

    output = []
    countries = defaultdict(int)
    for line in lines:
        
        wiki_name = path.basename(line.split('.wiki')[0])
#        wiki_name = file.replace('.wiki', '')
        
        oggs = re.findall('\|(?:audio=)?(?:\s*[a-zA-Z0-9_\-]+\s*=\s*)?([^\|:]+.ogg)', line)
        if len(oggs) == 0: continue

        cursor.execute('SELECT page_id FROM page WHERE page_title=%s', (wiki_name,))
        
        # cursor.execute('SELECT page_id FROM page WHERE page_title=%s', (wiki_name

        try:
            ids = cursor.fetchall()
            (id,) = ids[0]
        except errors.InterfaceError:
  #          print('fail on: %s' % line)
            continue
        except IndexError:
 #           print('no index for %s' % line)
            continue


        cursor.execute('SELECT gt_lat, gt_lon, gt_country FROM geo_tags WHERE gt_page_id=%s', (id,))

        try:
            coords = cursor.fetchall()
            lat, lon, country = coords[0]
        except (TypeError, IndexError) as e:
#            print('no coord for %s' % line.strip())
            continue

        if country != None:
            c = country.decode('utf-8')
            if countries[c] < 3:
                output.append((oggs[0], wiki_name, id, lat, lon))
            countries[c]+= 1

        # for ogg in oggs:
        #     output.append((ogg, wiki_name, id, lat, lon))

    with open('sound_files.tsv', 'w') as f:
        for line in sorted(output, key=lambda e: e[2]):
            f.write('%s\n' % ('\t'.join([str(i) for i in line])))

    cursor.close()
    db.close()

    #print(countries)
