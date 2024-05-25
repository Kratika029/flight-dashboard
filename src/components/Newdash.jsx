// import React from 'react'
import './Newdash.css'
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
// Fix for default marker icon not appearing
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;


const Newdash = () => {
  const [data, setData] = useState({});
  // const [routes, setRoutes] = useEffect([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
   
    const [selectedRoute, setSelectedRoute] = useState(null);
  // const [flightId, setFlightId] = useState('');
  // const [showDashboard, setShowDashboard] = useState(false);
  const postData = async () => {
    setLoading(true);
    setError(null);

    try {
        const response = await fetch('https://8785-2401-4900-1c2b-3d94-696b-b971-88ae-d60.ngrok-free.app/get_flight_id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              "flightid":"FDB1604"
          }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
       
        setData(result);
        // setRoutes(result.routes);
        console.log("abc", data.routes.coordinates);
    } catch (error) {
        setError(error.message);
    } finally {
        setLoading(false);
    }
};

useEffect(() => {
  postData();
}, []);
// useEffect(() => {
  // console.log("efj", data.routes[0][0][0][0]);
// }, [data]);

const handlePolylineClick = (route) => {
  setSelectedRoute(route);
};

const getColorByProbability = (probability) => {
  return probability > 0.7 ? 'green' : probability > 0.4 ? 'orange' : 'red';
};

const getColorByIntensity = (intensity) => {
  const redValue = Math.floor((intensity / 10) * 255);
  const green = 0;
  const blue = 0;
  return `rgba(${redValue}, ${green}, ${blue}, 0.5)`;
};


  return (
    <div className="page">
      
      <div>
        {/* {data} */}
      
        <div className="dashboard">
          <div className="column patches">
            <h3>Patches and Descriptions</h3>
            <ul>
              <li>Patch 1: Description 1</li>
              <li>Patch 2: Description 2</li>
              <li>Patch 3: Description 3</li>
            </ul>
          </div>
          <div className="column map">
            {/* <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: "400px", width: "100%" }}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={[51.505, -0.09]}>
                <Popup>
                  A sample marker.
                </Popup>
              </Marker>
            </MapContainer> */}
              <MapContainer
          center={[22.938, 68.7194  ]}
          zoom={6}
          style={{ height: "80%", width: "100%" }}
          scrollWheelZoom={true} // Enable scroll wheel zoom
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {/* <Marker position={flightData.start}>
            <Popup>
              Flight Start Position: {flightData.start[1]}, {flightData.start[0]}
            </Popup>
          </Marker>
          <Marker position={flightData.end}>
            <Popup>
              Flight End Position: {flightData.end[1]}, {flightData.end[0]}
            </Popup>
          </Marker> */}
          {/* {data.routes} */}
          {data.routes['coordinates'].map((route, index) => (
         <Polyline
         key={index}
         positions={route.map(point => [point[0], point[1]])}
         color={getColorByProbability(0.5)} // Placeholder for probability color
         eventHandlers={{
           click: () => handlePolylineClick(route),
         }}
       />
      ))}
          {/* Example weather conditions */}
          {/* <Circle
            center={[37.7749, -122.4194]}
            radius={50000} // in meters
            fillColor={getColorByIntensity(5)}
            fillOpacity={0.5}
            stroke={false}
          >
            <Popup>
              <b>Example Weather Condition</b><br />
              Intensity: 5
            </Popup>
          </Circle> */}
        </MapContainer> 
          </div>
          {/* <div className="column charts">
            <PieChartComponent title="Pie Chart 1" />
            <PieChartComponent title="Pie Chart 2" />
            <PieChartComponent title="Pie Chart 3" />
          </div> */}
        </div>
        
      
      </div>
    </div>
  );
};

const PieChartComponent = ({ title }) => {
  const data = [
    { name: 'Group A', value: 400 },
    { name: 'Group B', value: 300 },
    { name: 'Group C', value: 300 },
    { name: 'Group D', value: 200 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="pie-chart">
      <h4>{title}</h4>
      <PieChart width={400} height={400}>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
};

export default Newdash;
