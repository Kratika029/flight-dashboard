import json
import math
import random
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import time

app = Flask(__name__)
CORS(app, support_credentials=True)

SIGMET_URL = 'https://aviationweather.gov/api/data/isigmet?format=json'

SIGMET_DATA = {}
severity_criteria = {
        # Non-convective SIGMETs
        "OBSCTS": 0.6,
        "EMBDTS": 0.7,
        "FRQTS": 0.8,
        "SQLTS": 0.9,
        "OBSCTSGR": 0.7,
        "EMBDTSGR": 0.8,
        "FRQTSGR": 0.9,
        "SQLTSGR": 1.0,
        "SEVTURB": 0.9,
        "SEVICE": 0.9,
        "SEVICE (FZRA)": 0.9,
        "SEVMTW": 0.9,
        "HVYDS": 0.8,
        "HVYSS": 0.8,
        "RDOACTCLD": 0.9,
        # Convective SIGMETs
        "AREATS": 0.7,
        "LINETS": 0.8,
        "TDO": 0.9,
        "FC": 0.8,
        "WTSPT": 0.8,
        "HVY GR": 0.9,
    }

def getCentroid(polygon):
        x_coords = [point[0] for point in polygon]
        y_coords = [point[1] for point in polygon]
        _len = len(polygon)
        centroid_x = sum(x_coords) / _len
        centroid_y = sum(y_coords) / _len
        return centroid_x, centroid_y

def getSigmets():
    global SIGMET_DATA
    response = requests.get(SIGMET_URL)
    data = response.json()

    SIGMET_DATA = {}

    for sigmet in data:
        sigId = sigmet['isigmetId']

        coords = sigmet['coords']
        coords_list = []
        for coord in coords:
            lat, lon = coord['lat'], coord['lon']
            coords_list.append((lat, lon))

        centroid = getCentroid(coords_list)
        
        base = sigmet.get("base", 0)
        if not base:
            base = 0
        
        top = sigmet.get("top", 35000)
        if not top:
            top = 35000

        sigmetHazard = sigmet.get('qualifier', '') + sigmet.get('hazard', 'TS')

        severity_index = severity_criteria.get(sigmetHazard, random.uniform(0.5, 0.9))

        SIGMET_DATA[sigId] = {
             'sigId' : sigId,
             'coords' : coords_list,
             'centroid' : centroid,
             'base' : base,
             'top' : top,
             'sigmetHazard' : sigmetHazard,
             'severity_index' : severity_index
        }

def fetchSigmetsPeriodically():
    while True:
        print("REFRESHING SIGMET DATA")
        getSigmets()
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)

def haversine(c1, c2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = c1
    lat2, lon2 = c2

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Distance in kilometers
    distance = R * c
    
    return distance

@app.route('/getclosestSigmet', methods=['POST'])
def getclosestSigmet():
    data = request.json

    c1 = (data['lat'], data['lon'])
    altitude = data.get('altitude', 0)
    
    radius_of_search = data.get("radius_of_search", 250.0) # in kms

    closestSigmet = None

    for k, sigmet_data in SIGMET_DATA.items():
        # c2 = sigmet_data['centroid']
         for c2 in sigmet_data['coords']:
            haversine_dis = abs(haversine(c1, c2))
            if haversine_dis <= radius_of_search and altitude <= sigmet_data['top']:
                print(haversine_dis, c1, c2, sigmet_data['sigId'], altitude <= sigmet_data['top'])
                closestSigmet = sigmet_data
                break

    if not closestSigmet:
         return jsonify(None), 400

    print(c1, closestSigmet['centroid'])
    return jsonify(closestSigmet)

if __name__ == '__main__':
    sigmet_thread = threading.Thread(target=fetchSigmetsPeriodically)
    sigmet_thread.daemon = True
    sigmet_thread.start()

    app.run(host='0.0.0.0', debug=True, port=5006)
