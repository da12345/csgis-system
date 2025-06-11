import React from "react";

const SubmittedMapView = ({ setExploreMap, mapRef }) => {
  return (
    <div className="mapFullscreenContainer">
      <button
        type="button"
        onClick={() => setExploreMap(false)}
        style={{
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "5px",
          padding: "10px 20px",
          cursor: "pointer",
          position: "absolute",
          top: "10px",
          left: "10px",
          zIndex: 1001,
        }}
      >
        Back to Thanks
      </button>
      <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
};

export default SubmittedMapView;
