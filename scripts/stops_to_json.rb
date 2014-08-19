require 'nokogiri'
require 'json'

f = File.open("../official-data/stodvar.xml")

doc = Nokogiri::XML(f)

f.close

stops = []

doc.xpath("//stod").each do |s|
	stop = {}

	name = s["nafn"]
	short_name = name.split(" / ").last.split(" - ").last

	stop["name"] = name
	stop["short_name"] = short_name

	stop["latitude"] = s["lat"].to_f
	stop["longitude"] = s["lon"].to_f
	stop["id"] = s["id"]

	stops.push(stop)
end

File.open("../data/stops.json", "w") do |f|
  f.write(JSON.pretty_generate(stops))
end