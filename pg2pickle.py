"""
Create a pickle file for the output of a psql query like:
 psql wiki -q -c 'select x, y, count from en_pages_counts;' >pg_output

We assume that the type of the outputs is float!

Usage:
  pg2pickle.py <pg_output> [--output-dir=<d>]
  pg2pickle.py (-h | --help)
  pg2pickle.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --output-dir=<d>    Output file location [default: .]
"""


from docopt import docopt
from collections import defaultdict
import pickle

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

    output_filename = '%s.pickle' % (filename,)
    pickle.dump(data, open(output_filename, 'wb'))
    
