import datetime
import sqlite3
import time

conn = sqlite3.connect('mta.db', check_same_thread=False)

train_stop_times_sql = "select trips.trip_id, trips.route_id, trips.trip_headsign, stoptimes.arrival_time_seconds, stops.stop_name from gtfs_trips as trips \
join gtfs_stop_times as stoptimes on stoptimes.trip_id = trips.trip_id join gtfs_stops as stops on stoptimes.stop_id = stops.stop_id \
where stoptimes.stop_id in %s and stoptimes.trip_id in (select trip_id from gtfs_trips where service_id in (select service_id from \
gtfs_calendar where %s = 1)) order by stoptimes.arrival_time_seconds"

stops_sql = "select stop_id, stop_name from gtfs_stops where stop_name in %s"
colors = {'N': '#FCCC0A', 'R': '#FCCC0A', 'Q': '#FCCC0A', '1': '#EE352E', '2': '#EE352E', '3': '#EE352E', '4': '#00933C', \
'5': '#00933C', '6': '#00933C', 'B': '#FF6319', 'D': '#FF6319', 'F': '#FF6319', 'M': '#FF6319', 'A': '#2850AD', 'C': '#2850AD', \
'E': '#2850AD', 'G': '#6CBE45', 'J': '#996633', 'Z': '#996633', 'L': '#A7A9AC', '7': '#B933AD', 'S': '#808183'}

class SubwayTrip(object):

	trip_id = ""
	line = ""
	head = ""
	station = ""
	arrival_time = 0

	def __init__(self, row):
		self.trip_id = row[0]
		self.line = row[1]
		self.head = row[2]
		self.station = row[4]
	
		if int(row[3]) > 86400: self.arrival_time = int(row[3]) - 86400
		else: self.arrival_time = int(row[3])

	def getColors(self):
		color = colors[self.line]
		r = int(color[1:3], 16)
		g = int(color[3:5], 16)
		b = int(color[5:], 16)
		return r, g, b

def secs_since_midnight():
	now = datetime.datetime.now()
	secs = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
	return secs

def list_to_objects(train_list):
	triplist = []

	for train in train_list:
		triplist.append(SubwayTrip(train))

	output = sorted(triplist, key=lambda k: k.arrival_time)
	return output

def closest(target, collection):
	
	if target > 86400: target = target - 86400

	for train in collection:
		if train.arrival_time > target:
			return collection.index(train)
	return None

def get_trip_range(trip_list, low_time, high_time):
	start_index = closest(low_time, trip_list)
	end_index = closest(high_time, trip_list) - 1

	if end_index < start_index:
		trip_range = trip_list[start_index : ]
		for x in range(0, end_index):
			trip_range.append(trip_list[x])
	else:
		trip_range = trip_list[start_index : end_index]

	return trip_range

def get_train_schedule(stops): # TODO does not handle day wrapovers
	
	stops_list = "(%s)" % ','.join(["'%s'" % stops[stop] for stop in stops])
	stop_ids_raw = conn.execute(stops_sql % stops_list).fetchall()

	stop_ids = []
	for stop in stop_ids_raw:
		id = stop[0]
		name = stop[1]

		# print "\t", id, name

		for trunk in stops:

			# print "\t\t", trunk

			if id[0] in trunk and stops[trunk] == name:

				# print "\t\t\tFound", id
				
				stop_ids.append(id)
				break

	stop_ids = "(%s)" % ','.join(["'%s'" % entry for entry in stop_ids])
	return conn.execute(train_stop_times_sql % (stop_ids, time.strftime('%A').lower())).fetchall()

def get_trains_arriving_at(stops, start, to):
	
	arriving_trains_raw = get_train_schedule(stops)
	trips = list_to_objects(arriving_trains_raw)

	return get_trip_range(trips, start, to)
