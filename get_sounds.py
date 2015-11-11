"""
after something like:

egrep -R -o '(=|\|)([^\s]*\.ogg)' en/ >>sound_files_egrep

where en/ is a directory full of geotagged wiki source files.
Annoyingly the urls for files are not straight forward:

http://upload.wikimedia.org/wikipedia/commons/f/f1/Hu-Szeged.ogg

where f and f1 aren't constant. However,

https://en.wikipedia.org/wiki/File:Hu-Szeged.ogg

returns a HTML page with details of the file, which can be found 

"""

import re
from urllib import request, error

output_file = 'sound_urls_egrep'

with open(output_file) as f:
    original_lines = f.readlines()
    already = set([line.split('/')[-1].strip() for line in original_lines])

with open('sound_files_egrep') as f:
    oggs = re.findall('\|(?:audio=)?(?:\s*[a-zA-Z0-9_\-]+\s*=\s*)?([^\|:]+.ogg)', f.read())

done = 0
failed = 0
with open('sound_url_map', 'w') as f:

    for line in set(original_lines):
        f.write(line)

    for ogg in set(oggs).difference(already):
            
        url = 'https://en.wikipedia.org/wiki/File:' + request.quote(ogg)
        try:
            with request.urlopen(url) as res:
                page = res.read().decode('utf-8')
                match = re.search('//upload[^ ]+\.ogg', page, re.UNICODE)
                if match:
                    f.write('https:%s\n' % (match.group()))
                    print('%d: %s' % (done, match.group()))
                    done+= 1
        except error.HTTPError:
            print('404: %s' % ogg)
            failed+= 1

print('done %d, failed %d' % (done, failed))

        
