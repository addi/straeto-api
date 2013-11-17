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

class MainHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.get_all("latitude") and self.request.get_all("longitude"):
			latitude = float(self.request.get_all("latitude")[0])
			longitude = float(self.request.get_all("longitude")[0])

			radius = 500

			if self.request.get_all("radius"):
				radius = float(self.request.get_all("radius")[0])

			stopsInRadius = self.findStopsInRadius(latitude, longitude, radius)

			stopsWithTimes = self.addTimesToStops(stopsInRadius)

			prettyResponse = json.dumps(stopsWithTimes, indent=4, sort_keys=True)

			self.response.headers['Content-Type'] = 'application/json'

			self.response.write(prettyResponse)
		else:
			self.response.write('No lat/long :/')


	def addTimesToStops(self, stops):
		dayType = self.dayType()

		for stop in stops:
			stopFilePath = 'data/stops/{0}/{1}.json'.format(dayType, stop["stopId"])

			json_data = open(stopFilePath)

			data = json.load(json_data)

			stop["routes"] = data.values()

		return stops

	def dayType(self):
		weekDay = datetime.datetime.today().weekday()

		if weekDay < 5:
			dayType = "weekdays"
		elif weekDay == 5:
			dayType = "saturdays"
		else:
			dayType = "sundays"

		return dayType


	def findStopsInRadius(self, latitude, longitude, radius):

		json_data = open('data/allStops.json')

		data = json.load(json_data)

		stopsInRadius = []

		for stop in data:
			stopLatitude = stop["latitude"]
			stopLongitude = stop["longitude"]

			stopDistance = self.distance(latitude, longitude, stopLatitude, stopLongitude)

			if(stopDistance < radius):
				stop["distance"] = stopDistance

				stopsInRadius.append(stop)

		return sorted(stopsInRadius, key=lambda stop: stop["distance"])


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

		earthRadiusInMeters = 6378100
		return arc * earthRadiusInMeters


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
