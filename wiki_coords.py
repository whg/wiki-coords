import xml.etree.ElementTree as ET
from sys import stdout, argv
from glob import glob
import re
import psycopg2
import math

READ_STEP = 100
wikifile = 'svwiki-20151002-pages-articles.xml'
db_table = 'sv_pages'

class EndOfFileError(Exception):
    pass

def lat2y(a):
  return 180.0/math.pi*math.log(math.tan(math.pi/4.0+a*(math.pi/180.0)/2.0))

def grab_part(f, start_delimiter, end_delimiter, buffer=''):
    """
    return the bit we want and where to start from next time
    """
    
    while start_delimiter not in buffer:
        bit = f.read(READ_STEP)
        if len(bit) == 0:
            raise EndOfFileError
        buffer+= bit

    start = buffer.find(start_delimiter)
    buffer = buffer[start:]

    while end_delimiter not in buffer:
        bit = f.read(READ_STEP)
        if len(bit) == 0:
            raise EndOfFileError
            
        buffer+= bit

    end = buffer.find(end_delimiter) + len(end_delimiter)
    return (buffer[:end], buffer[end:])

def make_title(text):
    return text.replace(' ', '_').replace('/', ':')

amin = 1/60.0
asec = amin/60.0


def coordinate(latitude=None, lat=None, location_lat=None,
               longitude=None, long=None, location_lon=None,
               latd=None, lat_deg=None, lat_d=None, lat_degrees=None,
               latm=None, lat_min=None, lat_m=None, lat_minutes=None,
               lats=None, lat_sec=None, lat_s=None, lat_seconds=None,
               longd=None, lon_deg=None, long_d=None, long_degrees=None,
               longm=None, lon_min=None, long_m=None, long_minutes=None,
               longs=None, lon_sec=None, long_s=None, long_seconds=None,
               lat_direction=None, latNS=None, lat_NS=None, N_or_S=None,
               long_direction=None, longEW=None, long_EW=None, E_or_W=None,
               **kwargs):


    latitude = float(latitude or lat or location_lat or 0)
    longitude = float(longitude or long or location_lon or 0)

    if not latitude and not longitude:
        lat_degrees = latd or lat_deg or lat_d
        if lat_degrees == None:
            return None

        latd = float(lat_degrees)
        latm = float(latm or lat_min or lat_m or 0)
        lats = float(lats or lat_sec or lat_s or 0)
        
        lon_degrees = longd or lon_deg or long_d
        if lon_degrees == None:
            return None

        lond = float(lon_degrees)
        lonm = float(longm or lon_min or long_m or 0)
        lons = float(longs or lon_sec or long_s or 0)

        if latd == None or lond == None:
            return None

        latitude  = latd + latm * amin + lats * asec
        longitude = lond + lonm * amin + lons * asec

    NS = lat_direction or latNS or lat_NS or N_or_S
    if NS and NS.strip() == 'S':
        latitude*= -1

    EW = long_direction or longEW or long_EW or E_or_W
    if EW and EW.strip() == 'W':
        longitude*= -1

    if latitude and longitude:
        return latitude, longitude
        
cre = re.compile(r'(?:{{coord\|([^}]+)}})', re.IGNORECASE)

def get_coord(f):

    m = re.search(cre, f)

    try:
        data = m.groups(0)[0]

        if 'title' not in data:
            return None

        if 'globe' in data and 'globe:earth' not in data:
            return None

            
        bits = data.split('|')
        bits = [b for b in bits if '=' not in b and ':' not in b]
        
        if len(bits) < 2:
            return None

        # sometimes we get a bit like region here, chop it off
        # if len(bits[-1]) > 2:
        #     bits = bits[:-1]
        if len(bits) == 2:
            return coordinate(latitude=bits[0], longitude=bits[1])
        elif len(bits) == 4:
            return coordinate(latitude=bits[0], N_or_S=bits[1],
                              longitude=bits[2], E_or_W=bits[3])
        elif len(bits) == 6:
            return coordinate(latd=bits[0], latm=bits[1], N_or_S=bits[2],
                              longd=bits[3], longm=bits[4], E_or_W=bits[5])
        elif len(bits) == 8:
            return coordinate(latd=bits[0], latm=bits[1], lats=bits[2], N_or_S=bits[3],
                              longd=bits[4], longm=bits[5], longs=bits[6], E_or_W=bits[7])
        
    except AttributeError:
        pass

db = psycopg2.connect("dbname=wiki user=root")
cursor = db.cursor()
f = open(wikifile)
written = 0
withcoord = 0
already = set(glob('es_Wikipedia/*.wiki'))
regex = re.compile(r'latitude\s*=\s*(-?[0-9.]+)\s*\|\s*longitude\s*=\s*(-?[0-9.]+)\s')

ib_regex = re.compile(r'{{\s*Infobox[^}]*}}')
regex = re.compile(r'\|\s*(?:([a-zA-Z_]+)\s*=\s*([^|\n]*))')
crater_regex = re.compile('crater', re.IGNORECASE)
counter = 0
file_writes = 0
buffer = ''

def save(title, text, latlon):
    global file_writes

    lat, lon = latlon
    try:
        y = lat2y(float(lat))
    except ValueError:
        return


    cursor.execute('INSERT INTO '+db_table+' (page,lat,lon,x,y) VALUES (%s,%s,%s,%s,%s)', (title, lat, lon, lon, y)) 
    path = 'sv_Wikipedia/%s.wiki' % (title,)
    if path not in already:
        with open(path, 'w') as wf:
            wf.write(text)
            file_writes+= 1


if len(argv) >= 2:
    f.seek(int(argv[1]))
    print('seeked until %s' % argv[1])

try:
    while True:
        try:
            payload, remainder = grab_part(f, '<page>', '</page>', buffer)
        except EndOfFileError:
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
            coords = get_coord(text)
        except ValueError:
            continue

        if coords:
            save(title, text, coords)
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
                    save(title, text, latlon)
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

    print('\n\nfile at : ', f.tell())
    f.close()
    db.commit()
    cursor.close()
    db.close()
