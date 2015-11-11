"""
Usage:
  draw-points.py <language> [--output-dir=<d>] [--db=<db>]
  draw-points.py <language> <link-file> [--output-dir=<d>] [--db=<db>]
  draw-points.py (-h | --help)
  draw-points.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --output-dir=<d>    Output file location [default: www]
  --db=<db>     Database to use [default: wiki_pages]
"""
from docopt import docopt
from pyx import *
import math
import os
import psycopg2
from psycopg2.extensions import AsIs
from sys import stdout

if __name__ == "__main__":

    args = docopt(__doc__, version='0.1')
    # print(args)
    c = canvas.canvas()
    db = psycopg2.connect("dbname=%s user=root" % args['--db'])
    cursor = db.cursor()

    linkfile = args['<link-file>']
    
    if linkfile:
        import pickle
        with open(linkfile, 'rb') as f:
            links = pickle.load(f)

    cursor.execute('SELECT id, page, x, y FROM %s_pages;', (AsIs(args['<language>']),))
    places = dict([(id, (page, x, y)) for id, page, x, y in cursor.fetchall()])
         
                                                    
    added = 0
    size = 0.04
    d = 1
    col = color.rgb(0, 0, 0)
    c.stroke(path.rect(0, 0, 360*d, 360*d), [color.rgb(0.3, 0.3, 1)])

    if not linkfile:
        for id, (name, x, y) in places.items():

            if x < 180 and x > -180 and y > -180 and y < 180:
                c.fill(path.rect((x+180)*d, (y+180)*d, size, size), [col])
                added+=1


    else:

        max_depth = 9.0
        print(len(links.values()))
        from collections import defaultdict
        ordered = defaultdict(list)

        for id, depth in links.items():
            ordered[depth].append(id)

        for depth, ids in ordered.items():
            # cursor.execute('SELECT id, x, y FROM %s_pages WHERE id=%s', (AsIs(args['<language>']),id))
            # id, x, y = cursor.fetchone()
            print('depth: %d links %d' % (depth, len(ids)))

            c = canvas.canvas()
            col = color.rgb(0, 0, 0)
            c.stroke(path.rect(0, 0, 360*d, 360*d), [color.rgb(0.3, 0.3, 1)])

            added = 0
            for id in ids:
                _, x, y = places[id]

                if x < 180 and x > -180 and y > -180 and y < 180:
                    col = color.rgb(0,0,0) #color.hsb(depth/max_depth, 1.0, 0.8)
                    c.fill(path.rect((x+180)*d, (y+180)*d, size, size), [col])
                    added+= 1



            print('added %d places' % (added,))
            outputfile = '%s/%s-depth-%02d-points-%08d.pdf' % (args['--output-dir'], args['<language>'], depth, added);
            c.writePDFfile(outputfile)

    cursor.close()
    db.close()
