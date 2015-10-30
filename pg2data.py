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
    return '%s.%s' % (filename, type)

args = docopt(__doc__, version='0.1')
filename = args['<pg_output>']

try:
    with open(filename) as f:
        lines = f.readlines()
        
        
        if lines[1][0] != '-':
            column_names = [str(i) for i in range(lines[0].strip().count('|')+1)]
            line_slice = slice(0, -1)
        else:
            column_names = [p.strip() for p in lines[0].strip().split('|')]
            line_slice = slice(2, -2)

        data = defaultdict(list)

        for line in lines[line_slice]:
            parts = line.strip().split('|')
            for part, column in zip(parts, column_names):
                data[column].append(float(part.strip()))
except ValueError:
    print('ERROR: are you sure that the pg dump only contains floats?')
    exit()

if args['pickle']:
    import pickle

    pickle.dump(data, open(output_filename('pickle'), 'wb'))
    
elif args['fdata']:
    import struct
    from array import array

    with open(output_filename('fdata'), 'wb') as f:
        f.write(struct.pack('i', len(column_names)))
        f.write(struct.pack('i', len(data[column_names[0]])))

        for column in column_names:
            f.write(array('f', data[column]).tobytes())
        
