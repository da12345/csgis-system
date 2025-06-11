import React from "react";

const Introduction = ({ onNext }) => {
  return (
    <div
      style={{
        overflow: "hidden",
      }}
    >
      <h3>Introduction</h3>
      <p>
        In an aim to better understand people's perceptions of built environments, 
        we invite you to share your thoughts about the outdoor urban public space 
        you are currently in — one that affects your social well-being, either 
        positively or negatively. Your insights will help us understand how 
        urban spaces support well-being and social connections among people.
      </p>
      <p>
        On the map below, you can see places other people have been and 
        shared their thoughts about. Your location can be submitted even 
        if it has been previously submitted by someone else.
      </p>
      <p>
        Note: Make sure to give your browser permission to access your location. 
        Please switch on Wi-Fi, as it helps location accuracy, even if you 
        aren't connected to a network.
      </p>

      <h4 style={{ textAlign: "center", marginTop: "15px" }}>
        Take a look on the map below for inspiration.
      </h4>
      <h4 style={{ textAlign: "center", marginTop: "15px" }}>
        Ready to share? Let's get started!
      </h4>
      <h5 style={{ textAlign: "center", marginTop: "15px" }}>
        <i>
          By clicking "Next", I consent to share my location and feedback, and agree to the public display of my emoji rating and photo (if uploaded).
          For full details on how we handle your personal data, please see 
          <a href="https://docs.google.com/document/d/164lCkxVEJYFUjs2ChyWl8u5D_4jTNGF8/edit?usp=sharing&ouid=114067222048515852717&rtpof=true&sd=true" target="_blank" rel="noopener noreferrer"> this informational sheet</a>
        </i>
      </h5>
    </div>
  );
};

export default React.memo(Introduction);
