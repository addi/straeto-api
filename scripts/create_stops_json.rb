require 'nokogiri'
require 'json'


routes_xml = Nokogiri::XML(File.open("../official-data/leidir.xml"))

routes = {}

routes_xml.xpath("//leid").each do |r|

	route_id = r["lid"]
	route = r["num"]
	end_stop = r["leid"].split(" » ").last

	routes[route_id] = { "route" => route, "end_stop" => end_stop}

end

# p routes

doc = Nokogiri::XML(File.open("../official-data/ferlar.xml"))

stops_raw_data = {}

doc.xpath("//ferill").each do |f|

	f.xpath(".//variant").each do |v|

		variants = v["var"].split(",")

		v.xpath(".//stop").each do |s|

			stop = s["stod"]
			route_id = s["lid"]
			time = s["timi"]

			unless stops_raw_data.key?(stop)
				stops_raw_data[stop] = {}
			end

			unless stops_raw_data[stop].key?(route_id)
				stops_raw_data[stop][route_id] = {}
			end

			variants.each do |variant|
				unless stops_raw_data[stop][route_id].key?(variant)
					stops_raw_data[stop][route_id][variant] = []
				end
			end

			variants.each do |variant|
				unless stops_raw_data[stop][route_id][variant].include?(time)
					stops_raw_data[stop][route_id][variant] << time
				end
			end

		end
	end
end

# print stops_raw_data

stops = {}

stops_raw_data.each do |k, v|
	stops[k] = {}

	v.each do |kk, vv|
		day_types = {}

		vv.each do |kkk, vvv|
			
			time_hash = vvv.sort.join("").hash

			if day_types.key?(time_hash)
				day_types[time_hash]["day_types"] << kkk
			else

				tmp_time = vvv.sort

				after_midnight_count = 0

				tmp_time.each do |t|
					after_midnight_count += 1 if t.start_with?("00:")
				end

				if after_midnight_count > 0
					times = tmp_time[after_midnight_count..-1] + tmp_time[0, after_midnight_count]
				else
					times = tmp_time
				end

				day_types[time_hash] = {"day_types" => [kkk], "times" => times }
			end

		end 
		
		stops[k][kk] = { "route" => routes[kk]["route"], "last_stop_name" => routes[kk]["end_stop"], "day_types" => day_types.values() }

	end
end

stops.each do |stop_id, stop_data|
	File.open("../data/stops/"+stop_id+".json", "w") do |f|
		f.write(JSON.pretty_generate(stop_data))
	end
end

# print JSON.pretty_generate(stops["14001655"])

# File.open("../data/stops.json", "w") do |f|
#   f.write(JSON.pretty_generate(stops))
# end