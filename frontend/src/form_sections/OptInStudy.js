import React from "react";

const OptInStudy = ({ email, setEmail }) => {
  return (
    <div style={{ marginBottom: "30px" }}>
      <h3>Opt-in study (optional)</h3>
      <p>
        If you would like to participate in a further study, please enter your email below.
        This is optional. Your email will be linked to your responses to this questionnaire. If you are selected to participate, a new consent process will be carried out, and you will be rewarded for your time.
      </p>
      <input
        type="text"
        name="email"
        value={email || ""}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter email..."
        style={{
          width: "80%",
          padding: "8px",
          marginBottom: "10px",
          fontSize: "16px",
        }}
      />
    </div>
  );
};

export default OptInStudy;
