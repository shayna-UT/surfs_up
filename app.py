#########
# Run a Flask App:
#########
# from flask import Flask
# app = Flask(__name__)
# @app.route('/')
# def hello_world():
#     return 'Hello World'

#########
# Build a Climate App using Flask:
#########
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import extract
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
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    /api/v1.0/june-statistics
    /api/v1.0/december-statistics
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
	filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    temps = list(np.ravel(results))
	
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]           
    
    if not end: 
        results = session.query(*sel).\
            filter(Measurement.date <= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/june-statistics")
def june_statistics():
    results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs).\
        filter(extract('month', Measurement.date)==6).all()
    
    df = pd.DataFrame(results, columns=['date', 'precipitation', 'temperature'])
    df.set_index(df['date'], inplace=True)
    df = df.sort_index()
    
    june_stats = df.describe()
    june_stats_dict = june_stats.to_dict()

    return jsonify (june_stats_dict)

@app.route("/api/v1.0/december-statistics")
def dec_statistics():
    results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs).\
        filter(extract('month', Measurement.date)==12).all()
    
    df = pd.DataFrame(results, columns=['date', 'precipitation', 'temperature'])
    df.set_index(df['date'], inplace=True)
    df = df.sort_index()
    
    dec_stats = df.describe()
    dec_stats_dict = dec_stats.to_dict()

    return jsonify (dec_stats_dict)
