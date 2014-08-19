#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import math
import os
import datetime
import time

from google.appengine.api import memcache

class ScheduleHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Access-Control-Allow-Origin'] = '*'


		if self.request.get_all("latitude") and self.request.get_all("longitude"):
			latitude = float(self.request.get_all("latitude")[0])
			longitude = float(self.request.get_all("longitude")[0])

			radius = 500

			if self.request.get_all("radius"):
				radius = float(self.request.get_all("radius")[0])

			stops_in_radius = self.find_stops_in_radius(latitude, longitude, radius)

			pretty_response = json.dumps(stops_in_radius, indent=4, sort_keys=True)

			self.response.headers['Content-Type'] = 'application/json'			

			self.response.write(pretty_response)
		elif self.request.get_all("flush_cache"):
			flush_output = memcache.flush_all()

			self.response.write(flush_output)

		else:
			self.response.write('No lat/long :/')

	def bus_date(self):
		return datetime.datetime.utcnow() - datetime.timedelta(hours=1)

	def day_type(self):

		json_data = open('data/days.json')

		data = json.load(json_data)

		dateInfo = self.bus_date()

		day_key = '{0}-{1:02d}-{2:02d}'.format(dateInfo.year, dateInfo.month, dateInfo.day)

		# backup_day_type = (dateInfo.isoweekday() % 7) + 1

		return data.get(day_key, 0)

	def cache_time(self):
		current_bus_day_time = self.bus_date()

		cache_end_time = current_bus_day_time.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(hours=24)

		seconds_to_midnight = (cache_end_time - current_bus_day_time).seconds

		max_time = 60 * 60 * 6

		return max(seconds_to_midnight, max_time)

	def routes_for_stop(self, stop_id, day_type):

		stop_folder = stop_id[:1]

		stop_file_path = 'data/stops/{0}/{1}.json'.format(stop_folder, stop_id)

		print stop_file_path

		if os.path.exists(stop_file_path):
			json_data = open(stop_file_path)

			routes = json.load(json_data).values()

			for route in routes:

				for route_day_type in route["day_types"]:
					if day_type in route_day_type["day_types"]:
						route["times"] = route_day_type["times"]

				if route.get("times", None) == None:
					print "times not found"
					print route
					print "########"

				del route["day_types"]

			return routes
		else:
			return []

	# def add_time_to_stop(self, stop, day_type):
	# 	stop_file_path = 'data/stops/{0}.json'.format(stop["stop_id"])

	# 	if os.path.exists(stop_file_path):
	# 		json_data = open(stop_file_path)

	# 		routes = json.load(json_data).values()

	# 		routes = sorted(routes, key=lambda route: int(route["route"]))

	# 		stop["routes"] = self.add_current_times(routes)


	def add_current_times(self, routes):
		date_min = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
		date_max = date_min + datetime.timedelta(hours=2)
		
		min_mintues_into_the_day = date_min.hour * 60 + date_min.minute
		max_mintues_into_the_day = date_max.hour * 60 + date_max.minute

		items_to_delete = []

		for route in routes:
			# print "############"
			# print route
			# print "############"

			current_times = self.find_curent_time(route["times"], min_mintues_into_the_day, max_mintues_into_the_day)

			if current_times:
				route["current_times"] = self.find_curent_time(route["times"], min_mintues_into_the_day, max_mintues_into_the_day)
			else:
				items_to_delete.append(route)

		for dr in items_to_delete:
			routes.remove(dr)

		return routes

	def find_curent_time(self, times, min_mintues_into_the_day, max_mintues_into_the_day):

		for t, time in enumerate(times):
			hour, minute = map(int, time.split(":"))

			mintues_into_the_day = hour * 60 + minute

			# max_mintues_into_the_day < min_mintues_into_the_day is a shitmix to fix timeframes that overlap midnight
			if mintues_into_the_day >= min_mintues_into_the_day and (mintues_into_the_day <= max_mintues_into_the_day or max_mintues_into_the_day < min_mintues_into_the_day) :
				return times[t:t+6]

	def find_stops_in_radius(self, latitude, longitude, radius):

		cahcedInfo = memcache.get_multi(["day_type", "stops"])

		day_type = cahcedInfo.get("day_type", None)

		if day_type is None:
			print "day type is none!"

			day_type = self.day_type()

			memcache.add(key="day_type", value=day_type, time=self.cache_time())

		if day_type == 0:
			return []

		stops = cahcedInfo.get("stops", None)

		if stops is None:
			json_data = open('data/stops.json')

			stops = json.load(json_data)

			memcache.add(key="stops", value=stops)

		stops_in_radius = []
		stop_in_radius_keys = []

		for stop in stops:
			stop_latitude = stop["latitude"]
			stop_longitude = stop["longitude"]

			stop_distance = self.distance(latitude, longitude, stop_latitude, stop_longitude)

			if(stop_distance < radius):
				stop["distance"] = stop_distance

				stop["key"] = 'stop_{0}_{1}'.format(stop["id"], day_type)

				stops_in_radius.append(stop)
				stop_in_radius_keys.append(stop["key"])

		stops_in_radius_routes = memcache.get_multi(stop_in_radius_keys)

		for stop in stops_in_radius:

			stop_routes = stops_in_radius_routes.get(stop["key"], None)

			if stop_routes is None:
				stop_routes = self.routes_for_stop(stop["id"], day_type)

				memcache.add(key=stop["key"], value=stop_routes)

			print stop["id"]

			if stop["id"] == "90000295":
				print stop
				print stop_routes
				# print stop_routes

			stop["routes"] = self.add_current_times(stop_routes)

		return sorted(stops_in_radius, key=lambda stop: stop["distance"])

	def distance(self, lat1, long1, lat2, long2):

		# Convert latitude and longitude to 
		# spherical coordinates in radians.
		degrees_to_radians = math.pi/180.0
        
		# phi = 90 - latitude
		phi1 = (90.0 - lat1)*degrees_to_radians
		phi2 = (90.0 - lat2)*degrees_to_radians
        
		# theta = longitude
		theta1 = long1*degrees_to_radians
		theta2 = long2*degrees_to_radians
        
		# Compute spherical distance from spherical coordinates.
        
		# For two locations in spherical coordinates 
		# (1, theta, phi) and (1, theta, phi)
		# cosine( arc length ) = 
		#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
		# distance = rho * arc length
    
		cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
		arc = math.acos( cos )

		# Remember to multiply arc by the radius of the earth 
		# in your favorite set of units to get length.

		earth_radius_in_meters = 6378100

		distance = int(arc * earth_radius_in_meters)
		
		return distance


app = webapp2.WSGIApplication([
    ('/', ScheduleHandler),
    ('/schedule', ScheduleHandler)
], debug=True)
