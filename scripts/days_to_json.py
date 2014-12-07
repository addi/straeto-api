import json

from xml.dom import minidom

with open ("../official-data/dagar.xml") as myfile:
    data = myfile.read()

xmldoc = minidom.parseString(data)

itemlist = xmldoc.getElementsByTagName('dagur')

print len(itemlist)

days = {}

for d in itemlist:
	print d.attributes['dag'].value
	print d.attributes['variant'].value

	print ""

	days[d.attributes['dag'].value] = d.attributes['variant'].value

with open('../data/days.json', 'wb') as fp:
	json.dump(days, fp, indent=4, sort_keys=True)
