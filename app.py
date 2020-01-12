import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    session = Session(engine)
    precipitation = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
    group_by(Measurement.date).all()
    session.close()
    tobs_list = []
    for tobs in precipitation:
        tobs_dict = {}
        tobs_dict[tobs[0]] = round(tobs[1])
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    # Unravel results into a 1D array and convert to a list
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_data.append(station_dict)
    return jsonify(station_data)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session = Session(engine)

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)