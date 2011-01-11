#!/usr/bin/env python
# encoding: utf-8
import simplejson as json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

fp = open('departlist.json')
content = json.load(fp, encoding='utf-8')
fp.close()
content2="{\n"
for college in content.keys():
    for depart in content[college].keys():
        if depart == 'name':
            continue
        content2+= "\"" + college+depart + "\" : \"" + content[college][depart]+'\",'


content2 = content2[:-1] + "\n}"
fp = open('departlist2.json', 'w')
fp.write(content2)
fp.close()

