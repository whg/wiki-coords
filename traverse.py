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

print(len(maps))

def go(language, id, depth):

    # cursor.execute('SELECT to_id FROM %s_links WHERE from_id=%s', (AsIs(language), id))
    # to_ids = cursor.fetchall()
    
    to_ids = maps[id][:]

    if depth <= 0:
#         for id in to_ids:
#             if id not in output:
#                 output[id] = (id, depth)
#                 # output.add(id)
# # output.extend([(id[0], depth) for id in to_ids])
        return
        # return [id for id in to_ids]

    
    for tid in to_ids:
        go(language, tid, depth-1)
        if id not in output:
            output[tid] = (tid, depth)
            counts[depth]+= 1



def go2(from_id, maxdepth, depth=0):
    
    to_ids = maps[from_id]
    
    for to_id in to_ids:
        if to_id not in output:
            output[to_id] = depth
            counts[depth]+= 1

    if depth < maxdepth:
        for to_id in to_ids:
            go2(to_id, maxdepth, depth+1)

def go3(from_id, max_depth):

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

#res = go(language, id, depth)
output = go3(id, depth)

# ids = set([id for id, depth in output])
# print(len(ids))
print(len(output))

print(counts)
print(len(maps))

if not args['--dry-run']:
    with open('links-%s-%s.pickle' % (args['<page>'], depth), 'wb') as f:
        pickle.dump(output, f)

db.commit()
cursor.close()
db.close()

