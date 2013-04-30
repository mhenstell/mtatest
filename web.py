import time
import signal
import sys
from flask import Flask, render_template
import subway

app = Flask(__name__)
stops = {'123': 'Atlantic Av', '456': 'Atlantic Av', 'BDFM': 'Atlantic Av', 'ACE': 'Hoyt - Schermerhorn Sts', 'NRQ': 'Atlantic Av - Pacific St'}

def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	conn.close()
	sys.exit(0)

@app.route("/")
def hello():

	now = subway.secs_since_midnight()

	trip_range_5_10 = subway.get_trains_arriving_at(stops, start = now + 300, to = now + 600)
	trip_range_10_20 = subway.get_trains_arriving_at(stops, start = now + 600, to = now + 1200)
	trip_range_20_30 = subway.get_trains_arriving_at(stops, start = now + 1200, to = now + 1800)

	trip_ranges = [("5-10 Minutes", trip_range_5_10), ("10-20 Minutes", trip_range_10_20), ("20-30 Minutes", trip_range_20_30)]

	return render_template('index.html', trip_ranges = trip_ranges)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	app.debug = True
	app.run('0.0.0.0')