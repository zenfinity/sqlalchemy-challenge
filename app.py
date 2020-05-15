import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import datetime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/precipitation<br/>     returns a dict of last available full year of precipitation data<br/><br/>"
        f"/api/v1.0/stations<br/>      returns a list of the station names<br/><br/>"
        f"/api/v1.0/tobs<br/>      returns list of last full year of Temp Obs for most active station<br/><br/>"
        f"/api/v1.0/start<br/>      returns summary of low, high, and avg temps since date given<br/><br/>"
        f"/api/v1.0/start/end<br/>      returns summary of low, high, and avg temps between dates given<br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    lastDateStr = lastDate[0]

    lastDate = datetime.strptime(lastDateStr,"%Y-%m-%d")
    deltaOneYear = lastDate - dt.timedelta(days=365)
    deltaOneYearStr = deltaOneYear.strftime("%Y-%m-%d")

    query = session.query(Measurement.prcp, Measurement.date).\
        filter(Measurement.date > deltaOneYearStr).\
        order_by(Measurement.date).all()

    session.close()

    prcp = [t[0] for t in query]
    dates = [t[1] for t in query]
    prcp_dates = dict(zip(dates, prcp)) 

    return jsonify(prcp_dates)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query
    stationObsCounts = session.query(Measurement.station,func.count(Measurement.date)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date)).all()
    
    session.close()

    #Change result list of tuples to a list and Return a JSON list of stations from the dataset.
    station_names = [t[0] for t in stationObsCounts]

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #need to get the date to use in the query
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    lastDateStr = lastDate[0]
    #print(lastDateStr)
    lastDate = datetime.strptime(lastDateStr,"%Y-%m-%d")
    deltaOneYear = lastDate - dt.timedelta(days=365)
    deltaOneYearStr = deltaOneYear.strftime("%Y-%m-%d")
    print(deltaOneYearStr)
    #Get the station name
    stationObsCounts = session.query(Measurement.station,func.count(Measurement.date)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date)).all()
    heavyStation = stationObsCounts[0][0]
    print(heavyStation)
    #Query the dates and temperature observations of the most active station for the last year of data
    lastYearHeavyStation = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date > deltaOneYearStr).\
        filter(Measurement.station == heavyStation).\
        order_by(Measurement.date).all()
    print(lastYearHeavyStation)
    session.close()
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    
    tObservations = [t[1] for t in lastYearHeavyStation]
    print(tObservations)
    return jsonify(tObservations)


#/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`#http://127.0.0.1:5000/api/v1.0/2016-08-23
@app.route("/api/v1.0/<start>")
def summary_Start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get the station name
    stationObsCounts = session.query(Measurement.station,func.count(Measurement.date)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date)).all()
    heavyStation = stationObsCounts[0][0]

    lowTemp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.station == heavyStation).all()
    lowTemp = [t[0] for t in lowTemp]
    print(f"lowTemp is {lowTemp[0]}")

    highTemp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.station == heavyStation).all()
    highTemp = [t[0] for t in highTemp]
    print(f"highTemp is {highTemp[0]}")

    avgTemp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.station == heavyStation).all()
    avgTemp = [t[0] for t in avgTemp]
    print(f"avgTemp {avgTemp[0]}")

    session.close()

    #Making a dict instead of list so can more easily grab the values
    summaryStart = {"LowTemp"   : lowTemp[0],
                    "HighTemp"  : highTemp[0],
                    "AvgTemp"   : avgTemp[0]
                    }
    
    return jsonify(summaryStart)



@app.route("/api/v1.0/<start>/<end>")
def summary_StartEnd(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get the station name
    stationObsCounts = session.query(Measurement.station,func.count(Measurement.date)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date)).all()
    heavyStation = stationObsCounts[0][0]

    lowTemp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).\
        filter(Measurement.station == heavyStation).all()
    lowTemp = [t[0] for t in lowTemp]
    print(f"lowTemp is {lowTemp[0]}")

    highTemp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).\
        filter(Measurement.station == heavyStation).all()
    highTemp = [t[0] for t in highTemp]
    print(f"highTemp is {highTemp[0]}")

    avgTemp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date > start).\
        filter(Measurement.date < end).\
        filter(Measurement.station == heavyStation).all()
    avgTemp = [t[0] for t in avgTemp]
    print(f"avgTemp {avgTemp[0]}")

    session.close()

    #Making a dict instead of list so can more easily grab the values
    summaryStartEnd = {"LowTemp"   : lowTemp[0],
    "HighTemp"  : highTemp[0],
    "AvgTemp"   : avgTemp[0]
    }
    
    return jsonify(summaryStartEnd)

if __name__ == '__main__':
    app.run(debug=True)