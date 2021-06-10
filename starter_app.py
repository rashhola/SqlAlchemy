# Import everything you used in the starter_climate_analysis.ipynb file, along with Flask modules

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create an engine
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect an existing database into a new model with automap_base() and Base.prepare()

Base = automap_base()
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Instantiate a Session and bind it to the engine
session = Session(bind=engine)
#################################################
# Flask Setup
#################################################
# Instantiate a Flask object at __name__, and save it to a variable called app

app = Flask(__name__)
#################################################
# Flask Routes
#################################################
# Set the app.route() decorator for the base '/'
@app.route("/")

# define a welcome() function that returns a multiline string message to anyone who visits the route

def welcome():
    return  (
        f"Welcome to the Climate API!<br/>"
        f"<br/>"
        f"<br/>"
        f"The below routes are available via the climate API <br/>"
        f"> Precipitation<br/>"
        f"> Stations<br/>"
        f"> Temperature Observations<br/>"
        f"> Temperature Observation Statistics depending on inputed dates"
    )

# Set the app.route() decorator for the "/api/v1.0/precipitation" route
@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

# Calculate the date 1 year ago from last date in database
    last_datapoint_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_datapoint_date[0]
    One_year = datetime.strptime(last_datapoint_date[0],'%Y-%m-%d')- timedelta(days=365)
    One_year_fmt = One_year.strftime('%Y-%m-%d') 


# Query for the date and precipitation for the last year
    station_measurement = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > One_year_fmt).all()

# Create a dictionary to store the date: prcp pairs. 
    prcp_pairs = []
    for date, prcp in station_measurement:
        dict_row = {}
        dict_row["prcp"] = prcp
        dict_row["date"] = date
        prcp_pairs.append(dict_row)

    session.close()
    return jsonify(prcp_pairs)            

    
# Set the app.route() decorator for the "/api/v1.0/stations" route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_all = session.query(Station.station, Station.name).group_by(Station.station).all()
    stationlist = list(np.ravel(stations_all))
    session.close()
    return jsonify(stationlist)


# Unravel results into a 1D array and convert to a list
# Set the app.route() decorator for the "/api/v1.0/tobs" route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    last_datapoint_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    One_year = datetime.strptime(last_datapoint_date[0],'%Y-%m-%d')- timedelta(days=365)
    One_year_fmt = One_year.strftime('%Y-%m-%d')
    # station_measurement = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date > One_year_fmt).all()
    temperature = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= One_year_fmt).order_by(Measurement.date.asc()).all()
    tobs = []
    for station,date,temp in temperature:
        dict_row = {}
        dict_row["date"] = date
        dict_row["temp"] = temp
        dict_row["station"] = station
        tobs.append(dict_row)

    session.close()
    return jsonify(tobs)

  
# Set the app.route() decorator for the "/api/v1.0/temp/<start>" route and "/api/v1.0/temp/<start>/<end>" route
# define a stats() function that takes a start and end argument, and returns jsonified TMIN, TAVG, TMAX data from the database

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)
    if end is None:
        aggregates = func.min(Measurement.tobs).label("Min_Temp"),func.avg(Measurement.tobs).label("Avg_Temp"),func.max(Measurement.tobs).label("Max_Temp")
        temp_data = session.query(*aggregates).filter(Measurement.date >= start).all()
        list_temp = []
       
    
        for data in temp_data:
            dict_temp = {}
            dict_temp["minimum temperature"] = data.Min_Temp
            dict_temp["average temperature"] = data.Avg_Temp
            dict_temp["maximum temperature"] = data.Max_Temp
            list_temp.append(dict_temp)
            return jsonify(list_temp)
    else:
        aggregates = func.min(Measurement.tobs).label("Min_Temp"),func.avg(Measurement.tobs).label("Avg_Temp"),func.max(Measurement.tobs).label("Max_Temp")

        temp_data = session.query(*aggregates).filter(Measurement.date >= start). filter(Measurement.date <= end).all()

        temp_list = []

        for data in temp_data:
            dict_temp = {}
            dict_temp["minimum temperature"] = data.Min_Temp
            dict_temp["average temperature"] = data.Avg_Temp
            dict_temp["maximum temperature"] = data.Max_Temp
            temp_list.append(dict_temp)
            session.close()
            return jsonify(temp_list)
        
   

if __name__ == '__main__':
    app.run(debug=True)