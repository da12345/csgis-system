import React from "react";

const Photo = ({ handleFileChange, photoError, selectedFile, previewURL }) => {
    return (
        <div style={{ marginBottom: "20px" }}>
            <h3>Upload a Photo (optional)</h3>
            <p>Please take a photo of the place. Clicking below will open the camera if on a mobile device.</p>
            <p>To respect personal privacy, please avoid uploading pictures that include recognizable people.</p>
            <label style={{ 
                display: "inline-block", 
                padding: "10px 20px", 
                backgroundColor: "#4CAF50", 
                color: "white", 
                borderRadius: "5px", 
                cursor: "pointer", 
                marginTop: "10px" 
            }}>
                Take or choose a photo
                <input 
                    type="file" 
                    accept="image/*" 
                    capture="environment" 
                    onChange={handleFileChange} 
                    style={{ display: "none" }} 
                />
            </label>
            {previewURL && (
                <div style={{ marginTop: "0px" }}>
                    <p>Uploaded Photo:</p>
                    <img
                        src={previewURL}
                        alt="Uploaded preview"
                        style={{ width: "100%", maxWidth: "300px", borderRadius: "5px" }}
                    />
                </div>
            )}

            {photoError && <p style={{ color: "red" }}>{photoError}</p>}
        </div>
    );
};

export default Photo;
