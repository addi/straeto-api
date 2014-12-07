require 'nokogiri'
require 'json'
require 'fileutils'


routes_xml = Nokogiri::XML(File.open("../official-data/leidir.xml"))

routes = {}

routes_xml.xpath("//leid").each do |r|

	route_id = r["lid"]
	route = r["num"]
	end_stop = r["leid"].force_encoding('iso-8859-1').encode('utf-8').split(" » ").last

	routes[route_id] = { "route" => route, "end_stop" => end_stop}

end

# p routes

doc = Nokogiri::XML(File.open("../official-data/ferlar.xml"))

stops_raw_data = {}

doc.xpath("//ferill").each do |f|

	f.xpath(".//variant").each do |v|

		variants = v["var"].split(",")

		last_stops = {}
		
		# find last stops
		v.xpath(".//stop").each do |s|

			route_id = s["lid"]

			unless last_stops.key?(route_id)
				last_stops[route_id] = []
			end

			last_stops[route_id] << s["stnum"].to_i

		end

		stop_times = v.xpath(".//stop")

		stop_times.each_with_index do |s, index|

			stop = s["stod"]
			stop_number = s["stnum"].to_i
			route_id = s["lid"]
			time = s["timi"]

			next_stop = stop_times[index + 1]

			# remove arriving times
			if next_stop && next_stop["lid"] == route_id && next_stop["stod"] == stop
				# p "same stop, skip!"
				next
			end

			# Skip last stops in route
			if not next_stop || (last_stops.count > 1 &&  stop_number == last_stops[route_id].max)
				# p "skip"
				next
			end

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
	folder_name = stop_id.chars.first

	folder_path = "../data/stops/"+folder_name+"/"

	unless File.directory?(folder_path)
  		FileUtils.mkdir_p(folder_path)
	end

	File.open(folder_path+stop_id+".json", "w") do |f|
		f.write(JSON.pretty_generate(stop_data))
	end
end

# print JSON.pretty_generate(stops["14001655"])

# File.open("../data/stops.json", "w") do |f|
#   f.write(JSON.pretty_generate(stops))
# end