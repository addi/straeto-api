import json

from xml.dom import minidom

file_object = open('../official-data/dagar.xml')

# Fix the damn xml.
with open ("../official-data/dagar.xml") as myfile:
    data = myfile.read().replace('">', '"/>')

xmldoc = minidom.parseString(data)

itemlist = xmldoc.getElementsByTagName('dagur')

print len(itemlist)

days = {}

for d in itemlist:
	print d.attributes['dag'].value
	print d.attributes['variant'].value

	print ""

	days[d.attributes['dag'].value] = d.attributes['variant'].value

# print days

# pretty_response = json.dumps(days, indent=4, sort_keys=True)

# days_json = json.dumps(data) #, indent=4, sort_keys=True)


with open('../data/days.json', 'wb') as fp:
	json.dump(days, fp, indent=4, sort_keys=True)

# print days_json