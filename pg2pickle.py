"""
Create a pickle file for the output of a psql query like:
 psql wiki -q -c 'select x, y, count from en_pages_counts;' >pg_output

We assume that the type of the outputs is float!

Usage:
  pg2data.py pickle <pg_output> [--output-dir=<d>]
  pg2data.py fdata <pg_output> [--output-dir=<d>]
  pg2data.py (-h | --help)
  pg2data.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --output-dir=<d>    Output file location [default: .]
"""


from docopt import docopt
from collections import defaultdict

def output_filename(type):
    global filename
    output_filename = '%s.%s' % (filename, type)

args = docopt(__doc__, version='0.1')
filename = args['<pg_output>']

with open(filename) as f:
    lines = f.readlines()
    
    column_names = [p.strip() for p in lines[0].strip().split('|')]
    data = defaultdict(list)

    for line in lines[2:-2]:
        parts = line.strip().split('|')
        for part, column in zip(parts, column_names):
            data[column].append(float(part.strip()))


if args['pickle']:
    import pickle

    pickle.dump(data, open(output_filename('pickle'), 'wb'))
    
elif args['fdata']:
    import struct
    from array import array

    s = struct.pack('f', 4)
    size = struct.pack('i', 12)
    num = struct.pack('i', 2)
    
    numCols = len(data)
    numRows = len(data[data.keys()[0]))

    with open(output_filename('fdata'), 'wb') as f:
        f.write(struct.pack('i', len(column_names)))
        f.write(struct.pack('i', len(data[coloumn_names])))

        for column in column_names:
            f.write(array.fromlist(data[column].tobytes()))
        
