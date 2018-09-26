
# coding: utf-8

# # Building Climate app using Flask

# In[1]:


#Importing dependencies for plotting
import numpy as np
import pandas as pd
import datetime as dt


# In[3]:


# Importing Flask, Python SQL toolkit, and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify


# In[9]:


# Database Setup
engine = create_engine("sqlite:////Users/daryarudych/Desktop/repos/SQL-Python/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)


# In[ ]:


# Reflecting an existing database into a new model
Base = automap_base()
# Reflecting the tables
Base.prepare(engine, reflect=True)


# In[12]:


# Saving references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[13]:


# Creating our session (link) from Python to the DB
session = Session(engine)


# In[19]:


#Function to convert strings to date 
def str_to_date(date):
    return dt.datetime.strptime(date, "%Y-%m-%d").date()


# In[25]:


#Function to calculate min, avg, and max temperature for start/start-end dates
def normals(start, end):
    results = []
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return results


# In[8]:


# Using FLASK we create our routes.
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Climate app. Below is the list of available routes.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the dates and temperature observations from the last year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date.date, "%Y-%m-%d").date()
    prev_year =  last_date - dt.timedelta(days=365)
    prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=prev_year).filter(Measurement.date<=last_date).all()
    precipitation = dict(prcp)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station_list = []
    stations = session.query(Station.station).all()
    for s in stations:
        station_list.append(s) 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """"Return a JSON list of Temperature Observations (tobs) for the previous year."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date.date, "%Y-%m-%d").date()
    prev_year =  last_date - dt.timedelta(days=365)
    temps = session.query(Measurement.tobs).filter(Measurement.date>=prev_year).filter(Measurement.date<=last_date).all()
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def summary(start, end=None):
    summary = []
    try:
        summary_results = normals(start, end)
        summary.append(summary_results)
        return jsonify(summary) 
    except:
        print("Your date is incorrect")

if __name__ == "__main__":
    app.run(debug=True)

