import json
import math
from flask import Flask, request, jsonify
import random
import numpy as np
from queue import PriorityQueue
from typing import List, Tuple
import matplotlib
matplotlib.use('agg')
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv

load_dotenv()

import matplotlib.pyplot as plt
import folium
from IPython.display import display

app = Flask(__name__)
CORS(app, support_credentials=True)

FLIGHTAWARE_URL = "https://aeroapi.flightaware.com/aeroapi/flights/search"

import requests

def fetch_weather_data(lat, lon):
    api_key = os.environ['WEATHER_API_KEY']
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    # part = 'hourly,daily'
    # url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_score = normalize_weather(data)
        return weather_score
    else:
        # If the request fails, consider the weather as bad (0)
        return 0
    
def calculate_new_coordinates(lat, lon, distance_km, heading_deg):
    # Convert latitude and longitude from degrees to radians
    lat = math.radians(lat)
    lon = math.radians(lon)
    
    # Convert heading to radians
    heading = math.radians(heading_deg)
    
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Calculate the new latitude
    new_lat = math.asin(math.sin(lat) * math.cos(distance_km / R) +
                        math.cos(lat) * math.sin(distance_km / R) * math.cos(heading))
    
    # Calculate the new longitude
    new_lon = lon + math.atan2(math.sin(heading) * math.sin(distance_km / R) * math.cos(lat),
                               math.cos(distance_km / R) - math.sin(lat) * math.sin(new_lat))
    
    # Convert new latitude and longitude from radians to degrees
    new_lat = math.degrees(new_lat)
    new_lon = math.degrees(new_lon)
    
    return (new_lat, new_lon)

# FOR API 3.0 
# def normalize_weather(data):
#     current = data['current']

#     temp = current['temp']  # Temperature in Kelvin
#     wind_speed = current['wind_speed']  # Wind speed in m/s
#     weather_condition = current['weather'][0]['main']  # Main weather condition (e.g., Clear, Rain, etc.)

#     # Normalize temperature (let's assume 273K to 313K as 0 to 1)
#     temp_score = (temp - 273) / 40
#     temp_score = min(max(temp_score, 0), 1)  # Ensure the score is within [0, 1]

#     # Normalize wind speed (let's assume 0 to 20 m/s as 1 to 0)
#     wind_score = 1 - (wind_speed / 20)
#     wind_score = min(max(wind_score, 0), 1)  # Ensure the score is within [0, 1]

#     # Normalize weather condition
#     if weather_condition in ['Clear', 'Clouds']:
#         condition_score = 1
#     elif weather_condition in ['Drizzle', 'Rain']:
#         condition_score = 0.5
#     else:
#         condition_score = 0

#     # Combine scores with weights (feel free to adjust the weights)
#     weather_score = 0.5 * temp_score + 0.3 * wind_score + 0.2 * condition_score

#     return weather_score

def normalize_weather(data):
    # Initialize default values
    default_temp = 273  # Default temperature in Kelvin
    default_wind_speed = 0  # Default wind speed in m/s
    default_visibility = 10000  # Default visibility in meters
    default_cloudiness = 0  # Default cloudiness percentage
    default_precipitation = 0  # Default precipitation in mm
    default_condition = 'Clear'  # Default weather condition
    
    # Extract temperature, wind speed, visibility, cloudiness, precipitation, and weather condition from the data with defaults
    temp = data.get('main', {}).get('temp', default_temp)
    wind_speed = data.get('wind', {}).get('speed', default_wind_speed)
    visibility = data.get('visibility', default_visibility)
    cloudiness = data.get('clouds', {}).get('all', default_cloudiness)
    precipitation = data.get('rain', {}).get('1h', default_precipitation)
    weather_conditions = data.get('weather', [{'main': default_condition}])
    weather_condition = weather_conditions[0].get('main', default_condition)

    # Normalize temperature (assuming 273K to 313K as 0 to 1)
    temp_score = (temp - 273) / 40
    temp_score = min(max(temp_score, 0), 1)  # Ensure the score is within [0, 1]

    # Normalize wind speed (assuming 0 to 20 m/s as 1 to 0)
    wind_score = 1 - (wind_speed / 20)
    wind_score = min(max(wind_score, 0), 1)  # Ensure the score is within [0, 1]

    # Normalize visibility (assuming 0 to 10000 meters as 0 to 1)
    visibility_score = visibility / 10000
    visibility_score = min(max(visibility_score, 0), 1)  # Ensure the score is within [0, 1]

    # Normalize cloudiness (assuming 0% to 100% as 1 to 0)
    cloudiness_score = 1 - (cloudiness / 100)
    cloudiness_score = min(max(cloudiness_score, 0), 1)  # Ensure the score is within [0, 1]

    # Normalize precipitation (assuming 0 to 10 mm as 1 to 0)
    precipitation_score = 1 - (precipitation / 10)
    precipitation_score = min(max(precipitation_score, 0), 1)  # Ensure the score is within [0, 1]

    # Normalize weather condition
    if weather_condition in ['Clear']:
        condition_score = 1
    elif weather_condition in ['Clouds']:
        condition_score = 0.8
    elif weather_condition in ['Drizzle', 'Rain']:
        condition_score = 0.5
    else:
        condition_score = 0

    # Combine scores with weights (feel free to adjust the weights)
    weather_score = (0.1 * temp_score +
                     0.2 * wind_score +
                     0.4 * visibility_score +
                     0.1 * cloudiness_score +
                     0.1 * precipitation_score +
                     0.1 * condition_score)

    return weather_score

Waypoint = Tuple[int, int]
Path = List[Waypoint]

# Heuristic function for A* algorithm (Weighted Manhattan distance)
def heuristic(a: Waypoint, b: Waypoint) -> float:
    D = 1
    D2 = math.sqrt(2)

    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])

    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

# Get neighboring nodes in a grid (up, down, left, right, and diagonals)
def get_neighbors(node: Waypoint) -> List[Waypoint]:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]  # All eight directions
    neighbors = [(node[0] + d[0], node[1] + d[1]) for d in directions]
    return neighbors

# A* algorithm to find the shortest path with some variability and avoidance of bad weather
def a_star_search(start: Waypoint, goal: Waypoint, weather_conditions: np.ndarray) -> Path:
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not open_set.empty():
        _, current = open_set.get()

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path = tuple(path[::-1])
            return list(path)

        for neighbor in get_neighbors(current):
            if neighbor[0] < 0 or neighbor[1] < 0 or neighbor[0] >= weather_conditions.shape[0] or neighbor[1] >= weather_conditions.shape[1]:
                continue  # Skip out-of-bounds neighbors

            tentative_g_score = g_score[current] + 1 + random.uniform(0, 1) # Add randomness
            penalization_factor = 25 ** (1 - weather_conditions[neighbor[0], neighbor[1]]) + random.uniform(0, 10) # Randomize penalization factor

            # if weather_conditions[neighbor[0], neighbor[1]] <= 0.5:
            tentative_g_score += penalization_factor  # Penalize neighbors with bad weather

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))

    return []

# Find alternate paths attempting to avoid bad weather patches
def find_alternate_paths(start: Waypoint, goal: Waypoint, weather_conditions: np.ndarray, max_paths: int = 4) -> List[Path]:
    paths = []
    ratings = []
    while len(paths) < max_paths:
        path = a_star_search(start, goal, weather_conditions)
        if path:
            cur_path_rating = rate_paths([path], weather_conditions)[0]
            if cur_path_rating not in ratings:
                ratings.append(cur_path_rating)
                paths.append(path)
        else:
            break
    return paths, ratings

# [TESTING ONLY] Create weather patches on the grid
def create_weather_patches(grid_size: int, num_patches: int, max_radius: int) -> np.ndarray:
    weather_conditions = np.ones((grid_size, grid_size))

    for _ in range(num_patches):
        patch_radius = random.randint(max(0, max_radius-5), max_radius)
        patch_center = (random.randint(0, grid_size-1), random.randint(0, grid_size-1))
        val = random.uniform(0, 1)
        for i in range(-patch_radius, patch_radius+1):
            for j in range(-patch_radius, patch_radius+1):
                if 0 <= patch_center[0] + i < grid_size and 0 <= patch_center[1] + j < grid_size:
                    if abs(i) + abs(j) <= patch_radius:
                        weather_conditions[patch_center[0] + i, patch_center[1] + j] = val  # Bad weather

    return weather_conditions

# Rate paths based on weather suitability
def rate_paths(paths: List[Path], weather_conditions: np.ndarray) -> List[float]:
    path_ratings = []
    for path in paths:
        path_score = sum((1 - weather_conditions[waypoint[0], waypoint[1]]) for waypoint in path)  # Count good weather waypoints
        path_rating = len(path) + (25 ** path_score)  # Calculate rating based on the ratio of good weather waypoints
        path_ratings.append(path_rating)
    return path_ratings

def real_to_grid(latitude: float, longitude: float, start_location: tuple[float, float], end_location: tuple[float, float], grid_size: int = 7) -> tuple[int, int]:
    # Extract start and end coordinates
    start_lat, start_lon = start_location
    end_lat, end_lon = end_location
    
    # Calculate the scale factors for latitude and longitude directions
    scale_lat = (grid_size - 1) / (end_lat - start_lat)
    scale_lon = (grid_size - 1) / (end_lon - start_lon)
    
    # Transform the real-world coordinates to grid coordinates
    g_x = (latitude - start_lat) * scale_lat
    g_y = (longitude - start_lon) * scale_lon
    
    # Round the coordinates to the nearest integer
    g_x = int(round(g_x))
    g_y = int(round(g_y))
    
    return g_x, g_y

def grid_to_real(g_x: int, g_y: int, start_location: tuple[float, float], end_location: tuple[float, float], grid_size: int = 7) -> tuple[float, float]:
    # Extract start and end coordinates
    start_lat, start_lon = start_location
    end_lat, end_lon = end_location
    
    # Calculate the inverse scale factors for latitude and longitude directions
    scale_lat = (end_lat - start_lat) / (grid_size - 1)
    scale_lon = (end_lon - start_lon) / (grid_size - 1)
    
    # Transform the grid coordinates to real-world coordinates
    latitude = g_x * scale_lat + start_lat
    longitude = g_y * scale_lon + start_lon
    
    return round(latitude, 10), round(longitude, 10)

def fetch_and_normalize_weather_for_grid(grid_size: int, start_location, end_location, altitude) -> np.ndarray:
    weather_conditions = np.ones((grid_size, grid_size))

    weather_conditions_map = {}

    sigmets_identified = []
    unique_sigmets = set()

    for i in range(grid_size):
        for j in range(grid_size):
            lat, lon = grid_to_real(i, j, start_location, end_location, grid_size=grid_size) 

            weather_score = fetch_weather_data(lat, lon)
            # weather_score = random.uniform(0, 1)

            headers={
                'Content-type':'application/json', 
                'Accept':'application/json'
            }
            data = {
                "lat": lat,
                "lon": lon,
                "radius_of_search": 150,
                "altitude": altitude,
            }

            # closest_sigmet = requests.post("https://sigmetapi.onrender.com/getclosestSigmet", data=json.dumps(data), headers=headers)
            closest_sigmet = requests.post("http://localhost:5006/getclosestSigmet", data=json.dumps(data), headers=headers)

            if closest_sigmet.status_code == 200:
                # print("SIGMET DATA FOUND", lat, lon, closest_sigmet.json()['centroid'])
                sigData = closest_sigmet.json()

                if sigData['sigId'] not in unique_sigmets:
                    sigmets_identified.append(sigData)
                    unique_sigmets.add(sigData['sigId'])

                weather_score += -2.5

            weather_conditions_map[(lat, lon)] = weather_score
            
            weather_conditions[i, j] = weather_score

    weather_scaler = MinMaxScaler()

    weather_scores = np.array(list(weather_conditions_map.values())).reshape(-1, 1)

    weather_scaler.fit(weather_scores)

    scaled_weather_scores = weather_scaler.transform(weather_scores)

    weather_data_for_frontend = []
    for (lat, lon), scaled_score in zip(weather_conditions_map.keys(), scaled_weather_scores):
        weather_data_for_frontend.append([lat, lon, scaled_score[0]])

    # FOR 2D ARRAY
    weather_scores_flattened = weather_conditions.flatten().reshape(-1, 1)

    scaled_weather_scores_flattened = weather_scaler.transform(weather_scores_flattened)

    scaled_weather_scores_matrix = scaled_weather_scores_flattened.reshape(weather_conditions.shape)

    return scaled_weather_scores_matrix, weather_conditions, weather_data_for_frontend, sigmets_identified, (weather_scaler.data_min_, weather_scaler.data_max_)

def min_max_scaling(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    return (arr - min_val) / (max_val - min_val)

# Function to get optimal routes
def get_optimal_route(start_point, end_point, weather_conditions, grid_size=7):
    current_location = real_to_grid(start_point[0], start_point[1], start_point, end_point, grid_size)
    destination = real_to_grid(end_point[0], end_point[1], start_point, end_point, grid_size)
    
    alternate_paths, ratings = find_alternate_paths(current_location, destination, weather_conditions)
    
    real_paths = [[grid_to_real(g_x, g_y, start_point, end_point) for g_x, g_y in path] for path in alternate_paths]
    
    scaled_ratings = min_max_scaling(np.array(ratings))

    final_output = []
    for i, path in enumerate(real_paths):
        # final_output.append((path, scaled_ratings[i], "This is a sample description for Route " + str(i+1)))
        final_output.append({
            'coordinates': path,
            'rating':scaled_ratings[i],
            'description':"Description for Route " + str(i+1)
        })
        
    final_output = sorted(final_output, key = lambda x: x['rating'])

    return final_output

def visualize_grid(paths, weather_conditions, grid_size):
    fig, ax = plt.subplots()
    
    # Plot weather conditions
    cax = ax.matshow(weather_conditions, cmap='coolwarm')
    fig.colorbar(cax)
    
    # Plot paths
    for path in paths:
        x_coords = [point[0] for point in path]
        y_coords = [point[1] for point in path]
        ax.plot(y_coords, x_coords, marker='o')
    
    ax.set_title('Optimal Routes on Grid')
    ax.set_xlabel('Grid X')
    ax.set_ylabel('Grid Y')
    plt.show()

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)
    
def create_color(value):
    lightness = 1 - value
    # Multiply by 255 to get a value between 0 and 255 (appropriate for RGB)
    lightness_int = int(lightness * 255)
    # Convert lightness to a hex code (e.g., #FFFFFF for white) with zero padding
    color_code = f"#{lightness_int:02x}{lightness_int:02x}{lightness_int:02x}"
    return color_code

def visualize_real_world_map(paths, start_point, end_point, weather_points):
    map_ = folium.Map(location=[(start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2], zoom_start=7)
    
    # Add start and end points
    folium.Marker(location=start_point, popup='Start Point', icon=folium.Icon(color='green')).add_to(map_)
    folium.Marker(location=end_point, popup='End Point', icon=folium.Icon(color='red')).add_to(map_)
    
    for i in range(len(weather_points)):
        for j in range(len(weather_points[0])):
            folium.Circle(
                location=grid_to_real(i, j, start_point, end_point),
                radius=7500 * (1 - weather_points[i][j] if weather_points[i][j] >= 0 else weather_points[i][j] + 2.5),
                color="green" if weather_points[i][j] >= 0 else "blue",
                fill=True,
                fill_opacity= (1 - weather_points[i][j] if weather_points[i][j] >= 0 else 0.5),
            ).add_to(map_)
            # folium.Marker(location=grid_to_real(i, j, start_point, end_point), popup='End Point', icon=folium.Icon(color='red')).add_to(map_)

    colors = ['blue', 'red', 'green', 'black']

    # Plot paths
    for i, path_data in enumerate(paths):
        path, rating, desc = path_data['coordinates'], path_data['rating'], path_data['description']
        folium.PolyLine(path, color=colors[i], popup = rating, weight=(10 ** (1 - rating)) + 1.5, opacity= 1, smooth_factor = 0).add_to(map_)

    # Save map to an HTML file and display
    map_.save('map.html')
    display(map_)

@app.route('/get_flight_id', methods=['POST'])
@cross_origin(supports_credentials=True)
def getFlightbyId():
    data = request.json
    flight_id = str(data['flightid']).upper()
    grid_size = data.get('grid_size', 7)
    # data = {
    #         "flights": [
    #             {
    #                 "actual_off": "2024-05-24T14:33:32Z",
    #                 "actual_on": None,
    #                 "aircraft_type": "B38M",
    #                 "bounding_box": [
    #                     22.93801,
    #                     68.71938,
    #                     5.28623,
    #                     100.36844
    #                 ],
    #                 "destination": {
    #                     "airport_info_url": "/airports/OMDB",
    #                     "city": "Dubai",
    #                     "code": "OMDB",
    #                     "code_iata": "DXB",
    #                     "code_icao": "OMDB",
    #                     "code_lid": None,
    #                     "name": "Dubai Int'l",
    #                     "timezone": "Asia/Dubai"
    #                 },
    #                 "fa_flight_id": "FDB1604-1716387608-schedule-2426p",
    #                 "first_position_time": "2024-05-24T14:30:57Z",
    #                 "foresight_predictions_available": True,
    #                 "ident": "FDB1604",
    #                 "ident_iata": "FZ1604",
    #                 "ident_icao": "FDB1604",
    #                 "ident_prefix": None,
    #                 "last_position": {
    #                     "altitude": 380,
    #                     "altitude_change": "-",
    #                     "fa_flight_id": "FDB1604-1716387608-schedule-2426p",
    #                     "groundspeed": 475,
    #                     "heading": 110,
    #                     "latitude": 16.60658,
    #                     "longitude": 75.50421,
    #                     "timestamp": "2024-05-24T19:42:03Z",
    #                     "update_type": "A"
    #                 },
    #                 "origin": {
    #                     "airport_info_url": "/airports/WMKP",
    #                     "city": "George Town",
    #                     "code": "WMKP",
    #                     "code_iata": "PEN",
    #                     "code_icao": "WMKP",
    #                     "code_lid": None,
    #                     "name": "Penang Int'l",
    #                     "timezone": "Asia/Kuala_Lumpur"
    #                 },
    #                 "predicted_in": None,
    #                 "predicted_in_source": None,
    #                 "predicted_off": None,
    #                 "predicted_off_source": None,
    #                 "predicted_on": None,
    #                 "predicted_on_source": None,
    #                 "predicted_out": None,
    #                 "predicted_out_source": None,
    #                 "waypoints": []
    #             }
    #         ],
    #         "links": None,
    #         "num_pages": 1
    #     }
    
    # if flight_id != 'FDB1604':
    params = {
        'query' : '-identOrReg '+flight_id,
    }

    headers = {
        'x-apikey' : os.environ['FLIGHTAWARE_API_KEY'],
    }
    response = requests.get(FLIGHTAWARE_URL, params=params, headers=headers)
    data = response.json()
    
    
    if 'flights' not in data:
        return jsonify("The ID did not return any matching flights"), 400
    
    if len(data['flights']) == 0:
        return jsonify("The ID did not return any matching flights"), 400
    
    flight_data = data['flights'][0]['last_position']

    fa_flight_id = flight_data['fa_flight_id']
    altitude = flight_data['altitude']
    heading = flight_data['heading']
    lat = flight_data['latitude']
    lon = flight_data['longitude']
    
    start_location = (lat, lon)
    end_location = calculate_new_coordinates(lat, lon, 250.0, heading)
    
    flight_final_data = {
            "start_point": {
                "lat": start_location[0],
                "lon": start_location[1]
            },
            "end_point": {
                "lat": end_location[0],
                "lon": end_location[1],
            },
            "altitude": altitude,
            "fa_flight_id": fa_flight_id,
            'grid_size' : grid_size,
        }
    
    # Some redundant, toxic, not at all required, totally out of the world code ahead!
    # headers={
    #     'Content-type':'application/json', 
    #     'Accept':'application/json'
    # }
    # response_route = requests.post('http://localhost:5005/get_routes', data=json.dumps(flight_final_data), headers=headers)
    # if response_route.status_code != 200:
        # return jsonify("An Error Occured in Sub-Route"), 400
    output, code = get_routes_local_function(flight_final_data)
    return jsonify(output), code, 


# @app.route('/get_routes', methods=['POST'])
# @cross_origin(supports_credentials=True)
# def get_routes():
#     data = request.json 
#     print(data)
#     start_point = (data['start_point']['lat'], data['start_point']['lon'])
#     end_point = (data['end_point']['lat'], data['end_point']['lon'])
        
#     grid_size = 7

#     scaled_weather = actual_weather = create_weather_patches(grid_size, num_patches=7, max_radius=4)

#     # scaled_weather, actual_weather = fetch_and_normalize_weather_for_grid(grid_size, start_point, end_point)    

#     final_output = get_optimal_route(start_point, end_point, scaled_weather)
        
#     # Visualize on a real-world map
#     visualize_real_world_map(final_output, start_point, end_point, actual_weather)

#     return jsonify({
#         'routes': final_output,
#         'weather_conditions': actual_weather.tolist()
#     }), 200

def get_routes_local_function(data):
    start_point = (data['start_point']['lat'], data['start_point']['lon'])
    end_point = (data['end_point']['lat'], data['end_point']['lon'])
        
    grid_size = data.get('grid_size', 7)

    altitude = data['altitude']

    scaled_weather, actual_weather, map_scaled_weather, sigmets_identified, minmax = fetch_and_normalize_weather_for_grid(grid_size, start_point, end_point, altitude)    
    
    if minmax[1] < 0.5:
        return {
            'error_msg': "The entire Weather Matrix indicates that the path is not suitable for the Flying",
            'weather_conditions': map_scaled_weather,
        }, 305

    final_output = get_optimal_route(start_point, end_point, scaled_weather, grid_size=grid_size)
        
    visualize_real_world_map(final_output, start_point, end_point, actual_weather)
    
    return {
        'start_point': start_point,
        'end_point': end_point,
        'routes': final_output,
        'weather_conditions': map_scaled_weather,
        'sigmets':sigmets_identified,
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5005)
