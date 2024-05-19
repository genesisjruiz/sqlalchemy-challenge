# Climate Data API

#################################################
# Import Dependencies
#################################################
import numpy as np
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """All available routes."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Climate Data API</title>
    </head>
    <body>
      <h1>Climate Data API</h1>
      <p>Welcome to the Climate Data API! This API provides access to a range of weather-related information stored in our database. Here's what you can do with this API:</p>
      <ol>
        <li>Precipitation Data: Retrieve data on precipitation levels over a specific time period.</li>
        <li>Weather Stations: Access information about weather stations.</li>
        <li>Temperature Observations: Get temperature observations from our most active weather station.</li>
        <li>Dynamic Queries: Use dynamic routes to retrieve temperature statistics based on specified start and end dates.</li>
      </ol>
      <pTo get started, explore the available routes listed below or use the landing page to navigate the API endpoints.</p>
      <h2>Available Routes</h2>
      <ul>
        
        <li><a href="/api/v1.0/precipitation">Precipitation</a></li>
        <li><a href="/api/v1.0/stations">Weather Stations</a></li>
        <li><a href="/api/v1.0/tobs">Temperature Observations</a></li>
        <li><a href="/api/v1.0/<start">Start</a></li>
        <li><a href="/api/v1.0/<start>/<end">Start & End</a></li>

      </ul>
    </body>
    </html>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data for the last year."""
    # Calculate the date one year ago from the last date in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)

    # Query for the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()[0]

    # Calculate the date one year ago from the last date in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)

    # Query for the last 12 months of temperature observations for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {"date": date, "tobs": tobs}
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum, average, and maximum temperatures for a specified start date."""
    print(f"Received start date: {start}")
    try:
        dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    temperature_stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    if temperature_stats[0][0] is None:
        return jsonify({"error": "No data found for the given date range."}), 404

    temperature_stats_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
    return jsonify(temperature_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures for a specified start-end range."""
    print(f"Received start date: {start} and end date: {end}")
    try:
        dt.datetime.strptime(start, "%Y-%m-%d")
        dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    temperature_stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    if temperature_stats[0][0] is None:
        return jsonify({"error": "No data found for the given date range."}), 404

    temperature_stats_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
    return jsonify(temperature_stats_dict)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
