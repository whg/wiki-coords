"""
Usage:
  wiki_coords.py <wiki_file> [--seek=<b>] [--dry-run] [--db=<db>]
  wiki_coords.py (-h | --help)
  wiki_coords.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --seek=<b>    Seek to point in file [default: 0]
  --dry-run     Don't save to the database
  --db=<db>     Database to use [default: wiki]
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



def save(title, text, latlon, file_dir, dryrun):
    global file_writes
    lat, lon = latlon
    try:
        y = lat2y(float(lat))
    except ValueError:
        return False

    if not dryrun:
        cursor.execute('INSERT INTO %s (page,lat,lon,x,y) VALUES (%s,%s,%s,%s,%s)', (AsIs(db_table), title, lat, lon, lon, y)) 

    path = '%s2/%s.wiki' % (file_dir, title,)
    if path not in already_written:
        with open(path, 'w') as wf:
            wf.write(text)
        file_writes+= 1
    return True

def lang_from_file(filename):
    
    matches = re.findall(r'([a-z]+)wiki', filename)
    if matches:
        return matches[0]

def tablename(lang):
    return '%s_pages' % (lang,)

if __name__ == "__main__":
    args = docopt(__doc__, version='0.1')

    wikifile = args['<wiki_file>']
    language = lang_from_file(wikifile)
    db_table = tablename(language)
    file_directory = 'geo_pages/%s' % (language,)
    
    db = psycopg2.connect("dbname=%s user=root" % args['--db'])
    cursor = db.cursor()
    f = open(wikifile)

    written = 0
    withcoord = 0
    already_written = glob('%s/*.wiki' % (file_directory,))
    regex = re.compile(r'latitude\s*=\s*(-?[0-9.]+)\s*\|\s*longitude\s*=\s*(-?[0-9.]+)\s')

    ib_regex = re.compile(r'{{\s*Infobox[^}]*}}')
    regex = re.compile(r'\|\s*(?:([a-zA-Z_]+)\s*=\s*([^|\n]*))')
    crater_regex = re.compile('crater', re.IGNORECASE)
    counter = 0
    file_writes = 0
    buffer = ''


    if int(args['--seek']):
        f.seek(int(args['--seek']))
        print('seeked until %s' % args['--seek'])


    if not args['--dry-run']:
        try:
            cursor.execute('CREATE TABLE %s (id serial primary key, page text unique, lat real, lon real, x real, y real);' % db_table)
            db.commit()
            print('created table %s' %(db_table,))
        except psycopg2.ProgrammingError:
            print('table %s already exists' % db_table)
    
    try:
        while True:
            try:
                payload, buffer = grab_partn(f, '<page>', '</page>', buffer)
            except EOFError:
                break

            counter+= 1    
            xml = ET.fromstring(payload)
            
            
            if xml.find('redirect'):
                continue
    
            text = xml.find('revision/text').text
            if not text:
                continue
                
            title = make_title(xml.find('title').text)
            try:
                coords = wiki_coord(text)
            except ValueError:
                continue
    
            if coords:
                save(title, text, coords, file_directory, args['--dry-run'])
                withcoord+=1
                written+=1
                continue
    

            # infobox = re.findall(ib_regex, text)
            
            # if len(infobox) == 0 or not infobox[0]:
            #     continue

            # do this to filter out places like the moon            
            if re.search(crater_regex, text):
                continue
    
    
            match = re.findall(regex, text)
            if match:
                coord_args = dict(filter(lambda e: 'lat' in e[0] or 'lon' in e[0], match))
                
                try:
                    latlon = coordinate(**coord_args)
                    if latlon:
                        save(title, text, latlon, file_directory, args['--dry-run'])
                        written+= 1
    
                except ValueError:
                    pass
                
            stdout.write('\r%d: written %d (with coord %d, file writes: %d)' % (counter, written, withcoord, file_writes))
    except Exception as e:
        print('\n\nfile at : ', f.tell())

        import traceback
        traceback.print_exc(file=stdout)
        # import IPython
        # IPython.embed()
    finally:
        print(counter)
    
        print('file at : ', f.tell())
        f.close()
        db.commit()
        cursor.close()
        db.close()
