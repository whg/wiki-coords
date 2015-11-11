"""
Usage:
  traverse.py <language> <page> <depth> [--dry-run] [--db=<db>]
  traverse.py (-h | --help)
  traverse.py --version

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
from collections import defaultdict
import pickle

args = docopt(__doc__, version='0.1')

# print(args)
# exit()

language = args['<language>']
dry_run = args['--dry-run']
depth = int(args['<depth>'])

db = psycopg2.connect("dbname=%s user=root" % args['--db'])
cursor = db.cursor()

cursor.execute('SELECT page, id, x, y FROM %s_pages WHERE page=%s;', (AsIs(language), args['<page>']))

output = []
page, id, x, y = cursor.fetchone()
output.append([id, 0])

output = {}
maps = defaultdict(list)
counts = defaultdict(int)

cursor.execute('SELECT from_id, to_id FROM %s_links', (AsIs(language),))
for fro, to in cursor.fetchall():
    maps[fro].append(to)


def traverse(from_id, max_depth):

    output = {}
    
    to_ids = maps[from_id][:]
    
    for depth in range(max_depth):
        
        next_ids = []
        for id in to_ids:
            if id not in output:
                output[id] = depth
                counts[depth]+= 1

                next_ids.extend(maps[id][:])

        to_ids = next_ids[:]
        
    return output


output = traverse(id, depth)

print(len(output))

print(counts)
print(len(maps))

if not args['--dry-run']:
    with open('links-%s-%s.pickle' % (args['<page>'], depth), 'wb') as f:
        pickle.dump(output, f)

cursor.close()
db.close()

