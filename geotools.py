import math
import re

HC = 180.0/math.pi
QP = math.pi/4.0
QC = math.pi / 360.0

def lat2y(a):
    return HC * math.log(math.tan(QP + a * QC))



AMIN = 1/60.0
ASEC = AMIN/60.0


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

        lat_degrees = latd or lat_deg or lat_d or lat_degrees
        if lat_degrees == None:
            return None

        latd = float(lat_degrees)
        latm = float(latm or lat_min or lat_m or lat_minutes or 0)
        lats = float(lats or lat_sec or lat_s or lat_seconds or 0)
        
        lon_degrees = longd or lon_deg or long_d or long_degrees
        if lon_degrees == None:
            return None
            
        lond = float(lon_degrees)
        lonm = float(longm or lon_min or long_m or long_minutes or 0)
        lons = float(longs or lon_sec or long_s or long_seconds or 0)

        latitude  = latd + latm * AMIN + lats * ASEC
        longitude = lond + lonm * AMIN + lons * ASEC

    NS = lat_direction or latNS or lat_NS or N_or_S
    if NS and NS.strip() == 'S':
        latitude*= -1

    EW = long_direction or longEW or long_EW or E_or_W
    if EW and EW.strip() == 'W':
        longitude*= -1
    

    if latitude != None and longitude != None:
        return latitude, longitude


cre = re.compile(r'(?:{{coord\|([^}]+)}})', re.IGNORECASE)

def wiki_coord(f):

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
