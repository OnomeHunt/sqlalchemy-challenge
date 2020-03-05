# 1. imports
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
from datetime import timedelta
import dateutil.relativedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"


        
    )



# 4. Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Fetching the date and precipitation data and loading into dictionary """

   # get max date from measurement table
    max_date = session.query(func.max(Measurement.date).label('date')).first()
                        

    # convert to date
    max_date = datetime.strptime(max_date.date, '%Y-%m-%d')


    # Calculate the date 1 year ago from the last data point in the database
    last_12_months = (max_date-dateutil.relativedelta.relativedelta(months=12))

    prcp=[]
    dates=[]
    station=[]
    tobs=[]

    # Perform a query to retrieve the data and precipitation scores for the last year
    twelve_mths_data = session.query(Measurement.id,Measurement.station,Measurement.date,Measurement.prcp,Measurement.tobs
                                ).filter(Measurement.date>last_12_months)

    prcp_dict = {}
    for row in twelve_mths_data:
        prcp_dict[row.date] = row.prcp

    session.close()

       # JSON representation of dictionary
    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Fetching the stations data and loading into dictionary """

    stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations))

    session.close()

    return jsonify(stations_list)




@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Fetching the temperature data """
    # Design a query to find the temperature of last year

    max_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #convert max_date to date time format

    max_date = datetime.strptime(max_date.date, '%Y-%m-%d')

    # # Calculate the date 1 year ago from the last data point in the database
    months_12_ago =max_date - timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores for the last year
    data=session.query(Measurement).filter(Measurement.date >= months_12_ago).all()

    session.close()

    # Save the query results into a dictionary

    tobs_dict = {}
    for row in data:
        tobs_dict[row.date] = row.tobs

    # JSON representation of dictionary
    return jsonify(tobs_dict)



@app.route("/api/v1.0/<start_date>")
def temp_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Fetching the temperature data from start date"""
    # Calculate the lowest temperature recorded, highest temperature recorded, and average temperature

    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).first()[0]
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).first()[0]
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).first()[0]

    session.close()

    # Creating a dictionary to hold min, max and avg temperature values
    temp_dict = {}
    temp_dict['TMIN'] = min_temp
    temp_dict['TMAX'] = max_temp
    temp_dict['TAVG'] = avg_temp

    # JSON representation of dictionary
    return jsonify(temp_dict)




@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Fetching the temperature data between start date and end date"""
    # Calculate the lowest temperature recorded, highest temperature recorded, and average temperature

    lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()[0]
    highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()[0]
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()[0]

    session.close()

    # Creating a dictionary to hold min, max and avg temperature values
    temp_dict = {}
    temp_dict['TMIN'] = lowest_temp
    temp_dict['TMAX'] = highest_temp
    temp_dict['TAVG'] = avg_temp

    # JSON representation of dictionary
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)

