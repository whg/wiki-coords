"""
Usage:
  wiki_coords.py <wiki_file> [--seek=<b>]
  wiki_coords.py (-h | --help)
  wiki_coords.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --seek=<b>    Seek to point in file [default: 0]
"""

import xml.etree.ElementTree as ET
from sys import stdout, argv
from glob import glob
import re
import psycopg2
import math
from docopt import docopt

from geotools import coordinate, wiki_coord, lat2y
from util import grab_part, make_title



def save(title, text, latlon, file_dir):

    lat, lon = latlon
    try:
        y = lat2y(float(lat))
    except ValueError:
        return False

    cursor.execute('INSERT INTO '+db_table+' (page,lat,lon,x,y) VALUES (%s,%s,%s,%s,%s)', (title, lat, lon, lon, y)) 
    path = '%s/%s.wiki' % (file_dir, title,)
    if path not in already_written:
        with open(path, 'w') as wf:
            wf.write(text)

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
    
    db = psycopg2.connect("dbname=wiki user=root")
    cursor = db.cursor()
    f = open(wikifile)

    written = 0
    withcoord = 0
    already_written = set(glob('%s/*.wiki' % (file_directory,)))
    regex = re.compile(r'latitude\s*=\s*(-?[0-9.]+)\s*\|\s*longitude\s*=\s*(-?[0-9.]+)\s')

    ib_regex = re.compile(r'{{\s*Infobox[^}]*}}')
    regex = re.compile(r'\|\s*(?:([a-zA-Z_]+)\s*=\s*([^|\n]*))')
    crater_regex = re.compile('crater', re.IGNORECASE)
    counter = 0
    file_writes = 0
    buffer = ''

    
    if args['--seek']:
        f.seek(int(args['--seek']))
        print('seeked until %s' % args['--seek'])

    
    cursor.execute('CREATE TABLE %s (id serial primary key, page text unique, lat real, lon real, x real, y real);' % db_table)
    db.commit()
    print('created table %s', (db_table,))
    
    try:
        while True:
            try:
                payload, remainder = grab_part(f, '<page>', '</page>', buffer)
            except EOFError:
                break
                
            buffer = remainder
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
                save(title, text, coords, file_directory)
                withcoord+=1
                written+=1
                continue
    
            # do this to filter out places like the moon
            infobox = re.findall(ib_regex, text)
            
            if len(infobox) == 0 or not infobox[0]:
                continue
            
            if re.search(crater_regex, infobox[0]):
                continue
    
    
            match = re.findall(regex, infobox[0])
            if match:
                args = dict(filter(lambda e: 'lat' in e[0] or 'lon' in e[0], match))
                
                try:
                    latlon = coordinate(**args)
                    if latlon:
                        save(title, text, latlon, file_directory)
                        written+= 1
    
                except ValueError:
                    pass
                
            stdout.write('\r%d: written %d (with coord %d, file writes: %d)' % (counter, written, withcoord, file_writes))
    except Exception as e:
        print('\n\nfile at : ', f.tell())
        print(e)
        # import IPython
        # IPython.embed()
    finally:
        print(counter)
    
        print('\nfile at : ', f.tell())
        f.close()
        db.commit()
        cursor.close()
        db.close()
