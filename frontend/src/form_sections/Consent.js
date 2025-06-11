import React from "react";

const Consent = ({ isChecked, setIsChecked }) => {
  return (
    <div style={{ marginBottom: "15px" }}>
      <h3>Data collection consent</h3>
      <input
        type="checkbox"
        id="agree"
        checked={isChecked}
        onChange={() => setIsChecked(!isChecked)}
        style={{ marginRight: "8px" }}
      />
      <label htmlFor="agree" style={{ fontSize: "15px" }}>
        I agree to share the coordinates of the location I am currently at, submission time/date,
        and other information I choose to share in this questionnaire, in accordance with <a href="https://docs.google.com/document/d/164lCkxVEJYFUjs2ChyWl8u5D_4jTNGF8/edit?usp=sharing&ouid=114067222048515852717&rtpof=true&sd=true" target="_blank" rel="noopener noreferrer"> this informational sheet</a>
      </label>
    </div>
  );
};

export default Consent;
