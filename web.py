import time
import signal
import sys
from flask import Flask, render_template
from subway import *

app = Flask(__name__)
stops = {'123': 'Atlantic Av', '456': 'Atlantic Av', 'BDFM': 'Atlantic Av', 'ACE': 'Hoyt - Schermerhorn Sts', 'NRQ': 'Atlantic Av - Pacific St'}

# 5-10 min, 10-20 min, 20-30 min

def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	conn.close()
	sys.exit(0)

@app.route("/")
def hello():

	arriving_trains_raw = get_train_schedule(stops)
	trips = list_to_objects(arriving_trains_raw)

	now = secs_since_midnight()
	trip_range_5_10 = get_trip_range(trips, now + 300, now + 600)
	trip_range_10_20 = get_trip_range(trips, now + 600, now + 1200)
	trip_range_20_30 = get_trip_range(trips, now + 1200, now + 1800)

	trip_ranges = [("5-10 Minutes", trip_range_5_10), ("10-20 Minutes", trip_range_10_20), ("20-30 Minutes", trip_range_20_30)]

	return render_template('index.html', trip_ranges = trip_ranges, now = secs_since_midnight())

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	app.debug = True
	app.run('0.0.0.0')