import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Assign the measurement & station classes to local variables
measurement = Base.classes.measurement
station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return (
        f"<br/>"
        f"Welcome to hawaii weather station<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    # Query all stations names along with its code
    sel = [measurement.station, station.name]
    results = session.query(*sel)\
            .group_by(measurement.station).order_by(func.count(measurement.station).desc())\
            .filter(measurement.station == station.station)

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["code"] = stations.station
        stations_dict["name"] = stations.name
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return date & precipitation measurements from last year """

    #Find the date 12 months from the present
    year_ago = dt.date.today() - dt.timedelta(days=365)

    # Query for precipitation data for the previous year
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date > year_ago).\
            order_by(measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_stations
    last_year_prcp = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = prcp.date
        prcp_dict["precipitation"] = prcp.prcp
        last_year_prcp.append(prcp_dict)

    return jsonify(last_year_prcp)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return date & tobs measurements from last year """

    #Find the date 12 months from the present
    year_ago = dt.date.today() - dt.timedelta(days=365)

    # Query for precipitation data for the previous year
    results = session.query(measurement.date, measurement.tobs).\
            filter(measurement.date > year_ago).\
            order_by(measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_stations
    last_year_tobs = []
    for tobs_val in results:
        tobs_dict = {}
        tobs_dict["date"] = tobs_val.date
        tobs_dict["tobs"] = tobs_val.tobs
        last_year_tobs.append(tobs_dict)

    return jsonify(last_year_tobs)

@app.route("/api/v1.0/<start>/<end>")
def temperature(start,end):
    """Return minimum , average and the max temperature for a given start or start-end range. """

    results =  session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    temp = list(np.ravel(results))

    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)
