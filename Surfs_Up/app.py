# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2016,%208,%2023<br/>"
        f"/api/v1.0/start_end/2016,%208,%2023/2017,%208,%2023"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2016, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()
    
    session.close()
  
    precip_dict = {}
    for date in precip_data:
        precip_dict[date["date"]] = date["prcp"] 

    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create a query to return the list of stations
    stations = session.query(Station.station)

    session.close()

    station_list = []
    for station in stations:
        station_list.append(station[0])
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station
    temp_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).all()
    
    session.close()

    temp_list = []
    for date, tobs in temp_data:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['tobs'] = tobs
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)


@app.route("/api/v1.0/start/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    date_list = []
    results = session.query(Measurement.date).filter(Measurement.date).all()
    for result in results:
        date_list.append(result[0])

    start_date = start.replace(" ")
    for date in date_list:
        search_term = date["start"].replace(" ")
        if search_term == start_date:
            temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
            temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
            temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
            return jsonify (temp_min, temp_max, temp_avg)
    
        return jsonify({"error": "Date not found."}), 404

    session.close()


@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    date_list = []
    results = session.query(Measurement.date).filter(Measurement.date).all()
    for result in results:
        date_list.append(result[0])

    start_date = start.replace(" ")
    end_date = end.replace(" ")

    for date in date_list:
        start_search_term = date["start"].replace(" ")
        end_search_term = date["end"].replace(" ")
        if start_search_term == start_date and end_search_term == end_date:
            temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()
            temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all().all()
            temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all().all()
            return jsonify (temp_min, temp_max, temp_avg)
    
        return jsonify({"error": "Date not found."}), 404

    session.close()

    
if __name__ == '__main__':
    app.run(debug=True)
