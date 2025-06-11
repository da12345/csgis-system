import React from "react";

const DataCollectionInfo = ({ isOpen, handleClose }) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          padding: "20px",
          maxWidth: "500px",
          width: "90%",
          borderRadius: "8px",
        }}
      >
        <h2>Data collection</h2>
        <p>
          The information you choose to share on this website, including your
          location at this exact moment (not live location), will be publicly
          available. No personally identifiable information is collected, unless
          email is given, in which case this information will be shared only with
          relevant people at NTNU.
        </p>
        <button
          onClick={handleClose}
          style={{
            marginTop: "0px",
            padding: "10px 20px",
            fontSize: "16px",
            fontWeight: "bold",
            color: "white",
            backgroundColor: "#4CAF50",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Got it!
        </button>
      </div>
    </div>
  );
};

export default DataCollectionInfo;
