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

class ScheduleHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.get_all("latitude") and self.request.get_all("longitude"):
			latitude = float(self.request.get_all("latitude")[0])
			longitude = float(self.request.get_all("longitude")[0])

			radius = 500

			if self.request.get_all("radius"):
				radius = float(self.request.get_all("radius")[0])

			stops_in_radius = self.find_stops_in_radius(latitude, longitude, radius)

			# stops_with_Times = self.add_times_to_stops(stops_in_Radius)

			pretty_response = json.dumps(stops_in_radius, indent=4, sort_keys=True)

			self.response.headers['Content-Type'] = 'application/json'

			self.response.write(pretty_response)
		else:
			self.response.write('No lat/long :/')

	def add_time_to_stop(self, stop, day_type):
		stop_file_path = 'data/stops/{0}/{1}.json'.format(day_type, stop["stop_id"])

		json_data = open(stop_file_path)

		routes = json.load(json_data).values()

		stop["routes"] = self.add_current_times(routes)

	def day_type(self):

		dateInfo = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

		weekday = dateInfo.weekday()

		if weekday < 5:
			day_type = "weekdays"
		elif weekday == 5:
			day_type = "saturdays"
		else:
			day_type = "sundays"

		return day_type

	def add_current_times(self, routes):

		date_min = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
		date_max = date_min + datetime.timedelta(hours=2)
		
		min_mintues_into_the_day = date_min.hour * 60 + date_min.minute
		max_mintues_into_the_day = date_max.hour * 60 + date_max.minute

		items_to_delete = []

		for route in routes:
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
		day_type = self.day_type()

		json_data = open('data/allStops.json')

		data = json.load(json_data)

		stops_in_radius = []

		for stop in data:
			stop_latitude = stop["latitude"]
			stop_longitude = stop["longitude"]

			stop_distance = self.distance(latitude, longitude, stop_latitude, stop_longitude)

			if(stop_distance < radius):
				stop["distance"] = stop_distance

				self.add_time_to_stop(stop, day_type)

				if len(stop["routes"]) > 0:
					stops_in_radius.append(stop)

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
		return arc * earth_radius_in_meters


app = webapp2.WSGIApplication([
    ('/', ScheduleHandler),
    ('/schedule', ScheduleHandler)
], debug=True)
