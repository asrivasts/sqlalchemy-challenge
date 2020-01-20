from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Hawaii Travel API!</h1>"
        f"<h2 style=\"color:blue\">Available Routes:</h2>"
        f"<ul><li>/api/v1.0/precipitation<ul><li>Return the JSON representation of your dictionary</li></ul></li>"
        f"<li>/api/v1.0/stations<ul><li>Return a JSON list of stations from the dataset</li></ul></li>"
        f"<li>/api/v1.0/tobs<ul><li>query for the dates and temperature observations from a year from the last data point</li><li>Return a JSON list of Temperature Observations (tobs) for the previous year</li></ul></li>"
        f"<li>/api/v1.0/<i>start</i><ul><li>Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date</li><li>When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.</li></ul></li>"
        f"<li>/api/v1.0/<i>start</i>/<i>end</i><ul><li>Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date</li><li>When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.</li></ul></li></ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_query = session.query(Measurement.date.label("Date"), Measurement.prcp).all()
    session.close()

    measure_df = pd.DataFrame(prcp_query)
    measure_df.set_index(['Date'], inplace=True)

    results = {}
    for index,row in measure_df.iterrows():
        results[index] = dict(row)
    
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = session.query(Station.station.label("Station"), Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    
    station_df = pd.DataFrame(station_query)
    station_df.set_index(['Station'], inplace=True)

    results = {}
    for index,row in station_df.iterrows():
        results[index] = dict(row)
    
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    tobs_query = session.query(Measurement.date.label("Date"), Measurement.tobs).filter(Measurement.date >= year_ago.strftime("%Y-%m-%d")).order_by(Measurement.date).all()
    session.close()
    
    tobs_df = pd.DataFrame(tobs_query)
    tobs_df.set_index(['Date'], inplace=True)

    results = {}
    for index,row in tobs_df.iterrows():
        results[index] = dict(row)
    
    return jsonify(results)

#

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tripDuration(start, end='empty'):
    session = Session(engine)

    if(end == 'empty'):
        end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        

    trip_index = f"{start} to {end}"
   
    # Perform a query to retrieve the data and precipitation scores
    duration_query = session.query(func.min(Measurement.tobs).label("MinTemp"), func.max(Measurement.tobs).label("MaxTemp"), func.avg(Measurement.tobs).label("AvgTemp")).filter(Measurement.date.between(start, end)).all()
    session.close()
   
    duration_df = pd.DataFrame(duration_query)
    duration_df["info"] = [trip_index]
    duration_df.set_index(['info'], inplace=True)

    results = {}
    for index,row in duration_df.iterrows():
        results[index] = dict(row)
    
    return jsonify(results)
#    return(f"Start: {start} End: {end}")

if __name__ == "__main__":
    app.run(debug=True)
