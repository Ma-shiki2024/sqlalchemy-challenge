# Import the dependencies.
import numpy as np
import sqlalchemy
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from flask import Flask, jsonify

#database setup

#################################################
# Database Setup
#################################################
database_path = "../Resources/hawaii.sqlite"
engine = create_engine("sqlite:///hawaii.sqlite",pool_pre_ping=True)

# reflect an existing database into a new model
#reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
#create a dictionary of the active stations and their counts
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        station_data = []
        active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
        active_stations
        for station in active_stations:
            station_dict = {}
            station_dict["station name"] = station[0]
            station_data.append(station_dict)

        return jsonify(station_data)

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        prep_data = []
        cutoff_date = '2016-08-23'
        # Calculate the date one year from the last date in data set.
        prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
        prcp_df = pd.DataFrame(prcp)

        return jsonify(prcp_df.to_dict(orient="records"))

#app routing for t_observed for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    #create session link
    session = Session(engine)
    #query the last 12 months of temperature data from the most active observation station 
    cutoff_date_12month = '2016-08-23'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date_12month)).all()
    session.close()

    #create a dictionary of t_obs data for the most active station
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Oberved Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)