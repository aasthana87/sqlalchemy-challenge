# Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

# Database set-up
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask (__name__)

# Flask Routes
@ app.route("/")
def welcome():
    return (
        f"Welcome to Anji Asthana's Homework #10 - Flask Activity <br/> <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
    )

@ app.route("/api/v1.0/precipitation")
def precipitation():
    # Create link from Python to the database
    session = Session(engine)

    # Query data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Close session
    session.close()

    # Create a dictionary from results
    all_precipitation = []
    for result in results:
        measurement = {}
        measurement["date"] = result[0]
        measurement["prcp"] = result[1]
        all_precipitation.append(measurement)

    return jsonify(all_precipitation) 

@ app.route("/api/v1.0/stations")
def stations():
    # Create link from Python to the database
    session = Session(engine)

    # Query data
    results = session.query(Station.station).all()

    # Close session
    session.close()

    # Create  dictionary from results
    all_stations = []
    for result in results:
        station = {}
        station["station"] = result[0]
        all_stations.append(station)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create link from Python to the database
    session = Session(engine)

    # Define dates
    earliest_date = session.query(Measurement.date).order_by((Measurement.date)).limit(1).all()
    
    latest_date = session.query(Measurement.date).order_by((Measurement.date).desc()).limit(1).all()

    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query data
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= previous_year).order_by(Measurement.date).all()

    # Close session
    session.close()

    # Create dictionary from results
    previous_year_data = []
    for result in results:
        temp = {}
        temp["date"] = result[0]
        temp["tobs"] = result[1]
        previous_year_data.append(temp)

    return jsonify(previous_year_data)

@app.route("/api/v1.0/<start>", defaults={"end": None})
@app.route("/api/v1.0/<start>/<end>")
def date_range_temps(start, end):
    # Create link from Python to the database
    session = Session(engine)

    # Query data With both a start date and an end date
    if end != None:
        temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # With only a start date
    else:
        temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    # Close session
    session.close()

    # Convert results to a list
    temp_list = []
    no_temp_data = False
    for min_temp, max_temp, avg_temp in temp_data:
        if min_temp == None or max_temp == None or avg_temp == None:
            no_temp_data = True
        temp_list.append(min_temp)
        temp_list.append(max_temp)
        temp_list.append(avg_temp)

    if no_temp_data == True:
        return f"No temperature data found for the given date range. Please choose another date range."

    else:
        return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)