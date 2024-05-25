import React, {useState} from 'react'
import "./Airbus.css"
import logo from "../sentinels.png"
import Newdash from "./Newdash.jsx"
import Error from "./Error.jsx"
import banner from "../banner.png";

function Airbus() {
    const [flightId, setFlightId] = useState('');
  const [showDashboard, setShowDashboard] = useState(false);

  const handleButtonClick = () => {
    setShowDashboard(true);
  };
  

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
        <div className = "search">
        <input
          type="text"
          value={flightId}
          onChange={(e) => setFlightId(e.target.value)}
          placeholder="Enter Flight ID"
        />
        <button onClick={handleButtonClick}>Submit</button>
        
      </div>
    </div>
</div>
    </div>
    {showDashboard ? <Error flightId={flightId}/> : 
    <div className = "banner-area" style={{textAlign : "center"}}>
        <img src ={banner} alt = "banner" className="banner-image"/>
        <h2>Please Enter Flight ID</h2>
    </div>
    }
    </>
  )
}

export default Airbus