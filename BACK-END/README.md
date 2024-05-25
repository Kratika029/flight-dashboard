# Flight Route Optimization API

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [Get Flight ID Information](#get-flight-id-information)
  - [Get Flight Route](#get-flight-route)
- [Environment Variables](#environment-variables)
- [External APIs](#external-apis)
- [Dependencies](#dependencies)
- [License](#license)

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/flight-route-optimization.git
    cd flight-route-optimization
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root directory and add the necessary API keys:
    ```makefile
    WEATHER_API_KEY=your_openweathermap_api_key
    FLIGHTAWARE_API_KEY=your_flightaware_api_key
    ```

## Usage
Run the Flask app:
```sh
flask run
```

The API will be available at `http://127.0.0.1:5000/`.

## API Endpoints
### Get Flight ID Information

#### Request
```POST /get_flight_id```  
```json
{
    "flightid": "string",
    "grid_size": "int"
}
```

- flightid: The flight ID of the flight.
- grid_size: The size of the grid to be used for the flight route optimization.

#### Response
```json
{
  "start_point": {
    "lat": "float",
    "lon": "float"
  },
  "end_point": {
    "lat": "float",
    "lon": "float"
  },
  "routes": [
    {
      "coordinates": [[lat1, lon1], [lat2, lon2], ...],
      "rating": "float",
      "description": "string"
    },
    ...
  ],
  "weather_data": [
    [lat, lon, score],
    ...
  ],
  "sigmets": [
    {
      "sigId": "string",
      "centroid": {
        "lat": "float",
        "lon": "float"
      },
      ...
    }
    ...
  ]
}
```

- start_point: The starting point of the flight route.
- end_point: The ending point of the flight route.
- routes: The optimized flight routes.
- weather_data: The weather data for the flight route.
- sigmets: The SIGMETs for the flight route.


## Environment Variables
- `WEATHER_API_KEY`: The API key for OpenWeatherMap.
- `FLIGHTAWARE_API_KEY`: The API key for FlightAware.

## External APIs
- [OpenWeatherMap](https://openweathermap.org/api)
- [FlightAware](https://flightaware.com/commercial/flightxml/)
- [Aviation Weather Center](https://aviationweather.gov/)


## Dependencies
- [Flask](https://flask.palletsprojects.com/)
- [requests](https://docs.python-requests.org/en/master/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [geopy](https://geopy.readthedocs.io/en/stable/)
- [shapely](https://shapely.readthedocs.io/en/stable/)
- [pyproj](https://pyproj4.github.io/pyproj/stable/)
- [matplotlib](https://matplotlib.org/)
- [pandas](https://pandas.pydata.org/)
- [scikit-learn](https://scikit-learn.org/stable/)