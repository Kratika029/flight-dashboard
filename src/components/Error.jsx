import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Popup, Marker, Circle,  Polygon } from 'react-leaflet';
// import { MapContainer, TileLayer, Marker, Polyline, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Newdash.css'
const   Error = ({flightId}) => {
  const [routes, setRoutes] = useState([]);
  const [endPoints, setEndPoints] = useState([]);
  const [startPoints, setStartPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [weather, setWeather] = useState([]);
    // const[sigmets, setSigmets] = useState(null);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('https://58c0-2401-4900-1c2b-3d94-696b-b971-88ae-d60.ngrok-free.app/get_flight_id', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(
            {
              
                "flightid": flightId || "ASA538"
                // "flightid":i{flightId}
            } // Add any required data for the POST request
          ),
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setRoutes(data.routes);
        setEndPoints(data.end_point);
        setStartPoints(data.start_point);
        setWeather(data.weather_conditions)
        // setSigmets(data.sigmets)
        setLoading(false);
      } catch (error) {
        setError(error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);
  const getColorByProbability = (probability) => {
    return probability === 0 ? 'green' : probability < 0.4 ? 'grey' :   probability < 0.8 ? 'orange' : 'red';
  };

  const handlePolylineClick = (route) => {

    setSelectedRoute(route);
  };
  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="dashboard">
        <div className="column patches">
        {selectedRoute ? (
          <div>
            <h2>Route Details</h2>
            <p>{selectedRoute.description}</p>
            <p>Path Hinderance (between 0 and 1): {selectedRoute.rating}</p>
            {/* <p><strong>Path:</strong> {selectedRoute.map(point => `(${point[1]}, ${point[0]})`).join(' -> ')}</p> */}
          </div>
        ) : (
          <p>Select a route to see details</p>
        )}
            {/* <h3>Patches and Descriptions</h3>
            <ul>
              <li>Patch 1: Description 1</li>
              <li>Patch 2: Description 2</li>
              <li>Patch 3: Description 3</li>
            </ul> */}
          </div>
    
    <MapContainer center={endPoints} zoom={8} style={{ height: "100vh", width: "100%" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={startPoints}>
            <Popup>
              Flight Start Position: {startPoints[0]}, {startPoints[1]}
            </Popup>
          </Marker>
          <Marker position={endPoints}>
            <Popup>
              Flight End Position: {endPoints[0]}, {endPoints[1]}
            </Popup>
          </Marker>
      {routes.map((route, index) => (
        <Polyline key={index} positions={route.coordinates} 
        color={getColorByProbability(route.rating)}
        eventHandlers={{
            click: () => handlePolylineClick(route),
          }}>
          {/* <Popup>{route.description}</Popup> */}
         
        </Polyline>
      ))}


{weather.map((coord, index) => (
        <Circle
          key={index}
          center={[coord[0], coord[1]]}
          radius={(1-coord[2]) * 7500} // Assuming the rating is in kilometers, adjust the multiplier as needed
          fillColor="red"
          fillOpacity={0.5}
        >
          <Popup>Rating: {coord[2]}</Popup>
        </Circle>
      ))}


{/* <Polygon positions={sigmets.coords[0]} color="blue" /> */}
    </MapContainer>
    </div>
  );
};

export default Error;
