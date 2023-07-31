# Import the dependencies.
import matplotlib.pyplot as plt
import sqlalchemy
import json
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, render_template, jsonify



# Set the matplotlib style.
plt.style.use('fivethirtyeight')

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


# Flask Setup
app = Flask(__name__)

@app.route('/precipitation')
def profile():

    session = Session(engine)

    # Calculate the date 12 months ago from the current date
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= twelve_months_ago).\
              order_by(Measurement.date).all()

    session.close()

    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)    
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route('/base stations')
def login():
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Extracting the station names from the results
    station_names = [result[0] for result in results]

    # Return the station names as JSON response
    return jsonify({"stations": station_names})

@app.route('/active stations')
def active_stations():
    session = Session(engine)

    # Calculate the date 12 months ago from the current date
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query station name, date, and prcp data for the last year
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= twelve_months_ago).all()

    session.close()

    # Organize the data for each station
    station_data = {}
    for station, date, prcp in results:
        if station not in station_data:
            station_data[station] = []
        station_data[station].append({"date": date, "prcp": prcp})

    # Return the station data as JSON response
    return jsonify(station_data)

@app.route('/Min & Max & Avg Temp')
def temp():
    session = Session(engine)

    # Calculate the date 12 months ago from the current date
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Calculate the min, max, and average temp for the last 12 months
    results_last_12_months = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                             filter(Measurement.date >= twelve_months_ago).all()

    # Calculate the min, max, and average temp for the period before the last 12 months
    results_before_12_months = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                               filter(Measurement.date < twelve_months_ago).all()

    session.close()

    # Extract min_temp, max_temp, and avg_temp for the last 12 months
    min_temp_last_12_months, max_temp_last_12_months, avg_temp_last_12_months = results_last_12_months[0]

    # Extract min_temp, max_temp, and avg_temp for the period before the last 12 months
    min_temp_before_12_months, max_temp_before_12_months, avg_temp_before_12_months = results_before_12_months[0]

    # Return the min, max, and average temp for both periods as JSON response
    return jsonify({
        "last_12_months": {
            "min_temp": min_temp_last_12_months,
            "max_temp": max_temp_last_12_months,
            "avg_temp": avg_temp_last_12_months
        },
        "before_12_months": {
            "min_temp": min_temp_before_12_months,
            "max_temp": max_temp_before_12_months,
            "avg_temp": avg_temp_before_12_months
        }
    })

@app.route('/')
def home():
    routes = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods:
            routes.append(str(rule))
    return "Hawaii Weather API the following routes are as follows: " + ', '.join(routes)

if __name__ == '__main__':
    app.run(debug=True)
