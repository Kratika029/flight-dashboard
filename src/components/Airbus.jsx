import React, {useState, useEffect} from 'react'
import "./Airbus.css"
import logo from "../sentinels.png"
// import Newdash from "./Newdash.jsx"
import Error from "./Error.jsx"
import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';

import banner from "../banner.png";

function Airbus() {
    const [flightId, setFlightId] = useState('');
  const [showDashboard, setShowDashboard] = useState(false);
  const [sliderValue, setSliderValue] = useState(7);
  const handleButtonClick = () => {
    setShowDashboard(true);
  };
  const handleSliderChange = (e) => {
    setSliderValue(parseInt(e.target.value));
  };
  
useEffect(()=>{

},[showDashboard])
  return (
    <>
    <div className="header">
<div className="row">
    <div className="logo">
    <a href="/en" rel="home" class="site-logo">
<img src={logo} alt="Go to the home page" class="site-logo__img" width="300" height="80"/>
</a>
    </div>
    <div className="nav">
        {/* <ul className="nav-ul">
            <li className="nav-li">
                <a>About Us</a>
            </li>
            <li className="nav-li">
                <a>Description</a>
            </li>
        </ul> */}
        {/* <div className = "search">
        <input
          type="text"
          value={flightId}
          onChange={(e) => setFlightId(e.target.value)}
          placeholder="Enter Flight ID"
        />
        <button onClick={handleButtonClick}>Submit</button>
        
      </div> */}
    </div>
</div>
    </div>
    {showDashboard ? <Error flightId={flightId} gridSize={sliderValue}/> : 
    <div className = "banner-area" style={{textAlign : "center"}}>
        <img src ={banner} alt = "banner" className="banner-image"/>




        {/* <div className="flight-search-box">
      <div className="flight-search">
      <label htmlFor="flightId">Flight ID:</label>
        <input
          type="text"
          id="flightId"
          value={flightId}
          onChange={(e) => setFlightId(e.target.value)}
          placeholder="Enter Flight ID"
          className="flight-id-input"
        />
        <div className="slider-container">
         
          <label htmlFor="gridSize">Grid size:</label>
          <input
            type="range"
            id = "gridSize"
            min="4"
            max="10"
            value={sliderValue}
            onChange={handleSliderChange}
            className="slider"
          />
        </div>
        <button onClick={handleButtonClick} className="submit-button">Submit</button>
      </div>
    </div> */}
<div className="container" style={{display : "flex", flexDirection : "row", justifyContent :"center", alignItems : "center"}}>
  <form id="flight-form" >
    <div className="form-ele" style={{display : "flex", flexDirection : "row", justifyContent :"center", alignItems : "center", columnGap : "10px"}}>
    <label style= {{width : "100px"}} htmlFor="flight-id">Flight ID:</label>
        <input type="text" id="flight-id" name="flight-id"
        onChange={(e) => setFlightId(e.target.value)}
        required />
    </div>
    <div className="form-ele" style={{display : "flex", flexDirection : "row" , justifyContent :"center", alignItems : "center"}}>
    <label style= {{width : "350px"}} htmlFor="grid-size">Grid Size:</label>
    <Slider
                value={sliderValue}
                onChange={handleSliderChange}
                aria-label="Small steps"
                valueLabelDisplay="auto"
                step={1}
                marks
                min={4}
                max={10}
              />
        <span id="grid-size-label">{sliderValue}</span>
    </div>
    <div className="form-ele">
    <button onClick={handleButtonClick} type="submit">Analyze</button>
    </div>
  </form>
</div>


        




    </div>
    }
    </>
  )
}

export default Airbus