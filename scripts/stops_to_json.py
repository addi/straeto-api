import json

import sys

# from xml.dom import minidom
import xml.etree.ElementTree as ET


file_path = "../official-data/stodvar-utf8.xml"

#stops_data = open(file_path).read() .decode('iso-8859-1') #.encode('utf-8')

#print stops_data


tree = ET.parse(file_path)

for neighbor in tree.iter('stod'):
	print neighbor.attrib

# xmldoc = minidom.parse(file_path)

# #xmldoc = minidom.parseString(stops_data)


# itemlist = xmldoc.getElementsByTagName('stod')



# stops = []

# for s in itemlist:
# 	stop = {}

# 	name = s.attributes['nafn'].value
# 	short_name = name.split(" / ")[-1]

# 	stop['name'] = name #.encode("iso-8859-1")
# 	stop['short_name'] = short_name #.encode("iso-8859-1")

# 	print type(name)
# 	print name

# 	# print str(stop)
# 	print stop

# 	print ""

# 	print stop
# 	stops.append(stop)

# 	# break

# with open('../data/stops.json', 'wb') as fp:
# 	#s = json.dumps(stops)
# 	json.dump(stops, fp, indent=4, sort_keys=True)
# 	#fp.write(s)
# 	#fp.flush()

# # print stops

