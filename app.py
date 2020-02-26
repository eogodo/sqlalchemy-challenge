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
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    prcp_dict = {}
    for date, prcp in results:      
        prcp_dict[date] = prcp
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    session = Session(engine)
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()

    stations_list = []
    for result in results: 
        stations_list.append(result[0])

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date,'%Y-%m-%d').date()
    year_ago = last_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=year_ago).all()
    session.close()

    temp_list = []
    for result in results:
        temp_list.append(result[1])

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>",defaults={'end':None})
@app.route("/api/v1.0/<start>/<end>")
def vacay(start,end):
    session = Session(engine)
    if end == None: 
        end = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0],'%Y-%m-%d').date()
    else: 
        end = dt.datetime.strptime(end, "%Y-%m-%d").date()

    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date<=end).all()
    session.close()

    return jsonify(results[0])


if __name__ == '__main__':
    app.run(debug=True)