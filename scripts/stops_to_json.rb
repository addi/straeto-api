require 'nokogiri'
require 'json'

f = File.open("../official-data/stodvar.xml")

doc = Nokogiri::XML(f)

f.close

stops = []

doc.xpath("//stod").each do |s|
	stop = {}

	name = s["nafn"].force_encoding('iso-8859-1').encode('utf-8')

	p name

	short_name = name.split(" / ").last.split(" - ").last

	stop["name"] = name
	stop["long_name"] = name
	stop["short_name"] = short_name

	stop["latitude"] = s["lat"].to_f
	stop["longitude"] = s["lon"].to_f
	stop["id"] = s["id"]

	stops.push(stop)
end

File.open("../data/stops.json", "w") do |f|
  f.write(JSON.pretty_generate(stops))
end