"""
Usage:
  draw-points.py <language> [--output-dir=<d>] [--db=<db>]
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

if __name__ == "__main__":

    args = docopt(__doc__, version='0.1')
    # print(args)
    c = canvas.canvas()
    db = psycopg2.connect("dbname=%s user=root" % args['--db'])
    cursor = db.cursor()
    
    cursor.execute('SELECT id, page, x, y FROM %s_pages;', (AsIs(args['<language>']),))
    places = cursor.fetchall()
                                                             


    added = 0
    size = 0.1
    d = 1
    col = color.rgb(0, 0, 0)
    for id, name, x, y in places:

        if x < 180 and x > -180 and y > -180 and y < 180:
            c.fill(path.rect((x+180)*d, (y+180)*d, size, size), [col])
            added+=1

    print('added %d places' % (added,))

    outputfile = '%s/%s-points-%d.pdf' % (args['--output-dir'], args['<language>'], added);
    c.writePDFfile(outputfile)

    cursor.close()
    db.close()
