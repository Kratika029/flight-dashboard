import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Popup, Marker, Circle,  Polygon } from 'react-leaflet';
import Loader from "./loader";
// import { MapContainer, TileLayer, Marker, Polyline, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Newdash.css'
const   Error = ({flightId, gridSize}) => {
  const [routes, setRoutes] = useState([]);
  const [endPoints, setEndPoints] = useState([]);
  const [startPoints, setStartPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [weather, setWeather] = useState([]);
  const [showBestRoute, setShowBestRoute] = useState(false);
  const [showWeather, setShowWeather] = useState(false);
  const [showSigmet, setShowSigmet] = useState(false);
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
              
                "flightid": flightId || "ASA538",
                "grid_size" : gridSize || 7
                
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

  const handleToggleBestRoute = () => {
    setShowBestRoute(!showBestRoute);
  };

  const handleToggleWeather = () => {
    setShowWeather(!showWeather);
  };

  const handleToggleSigmet = () => {
    setShowSigmet(!showSigmet);
  };
  const getColorByProbability = (probability) => {
    return probability === 0 ? 'green' : probability < 0.4 ? 'grey' :   probability < 0.8 ? 'orange' : 'red';
  };

  const handlePolylineClick = (route) => {

    setSelectedRoute(route);
  };
  if (loading) {
    return(
      <div style={{display : "flex", flexDirection : "column", marginTop: "200px", justifyContent : "center"}}>
<div
    style={{
      display : "flex", flexDirection : "column",
        width: "100px",
        // height : "500px",
        margin: "auto",
    }}
>
    <Loader />
    
    
</div>
<div style={{display : "flex", width: "700px",
       margin: "auto", justifyContent : "center"}}>
    <p >Plotting the Perfect Path... A Storm-Free Express! </p>
    </div>
      </div>
     )
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <div className="toggle-container">
        <div style={{display : "flex", flexDirection : "row", alignItems :"center", columnGap : "8px"}}>
      <p>Show Best Route:</p>
          <label class="switch">
            
            <input
              type="checkbox"
              checked={showBestRoute}
              onChange={handleToggleBestRoute}
            />
            <span class="slider round"></span>
          </label>
          </div>

          <div style={{display : "flex", flexDirection : "row", alignItems :"center", columnGap : "8px"}}>
          <p>Show Weather:</p>
          <label class="switch">
            
            <input
              type="checkbox"
              checked={showWeather}
              onChange={handleToggleWeather}
            />
            <span class="slider round"></span>
          </label>
          </div>



          {/* <div style={{display : "flex", flexDirection : "row", alignItems :"center", columnGap : "8px"}}>
          <p>Show SIGMET:</p>
          <label>
           
            <input class="switch"
              type="checkbox"
              checked={showSigmet}
              onChange={handleToggleSigmet}
            />
            <span class="slider round"></span>
          </label>
          </div> */}




        </div>
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
            
          </div>
    
    <MapContainer center={endPoints} zoom={8} style={{ height: "100vh", width: "100%" , margin : "10px"}}>
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

          {showBestRoute ? (
  routes
    .filter(route => route.rating === 0)
    .map((route, index) => (
      <Polyline
        key={index}
        positions={route.coordinates}
        weight={10 ** (1-route.rating)}
        color={getColorByProbability(route.rating)}
        eventHandlers={{
          click: () => handlePolylineClick(route),
        }}
      >
        <Popup>{route.description}</Popup>
      </Polyline>
    ))
) : (
  routes.map((route, index) => (
    <Polyline
      key={index}
      positions={route.coordinates}
      weight={10 ** (1-route.rating)}
      color={getColorByProbability(route.rating)}
      eventHandlers={{
        click: () => handlePolylineClick(route),
      }}
    >
      {/* <Popup>{route.description}</Popup> */}
    </Polyline>
  ))
)}


{showWeather && weather.map((coord, index) => (
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
    </div>
  );
};

export default Error;
