import React from "react";

const Gender = ({ selectedGender, setSelectedGender }) => {
  const genders = ["Male", "Female", "Other"];

  return (
    <div style={{ marginBottom: "30px" }}>
      <h3>Gender</h3>
      {genders.map((gender) => (
        <div key={gender} style={{ marginBottom: "8px" }}>
          <input
            type="radio"
            id={gender}
            name="gender"
            value={gender}
            checked={selectedGender === gender}
            onChange={() => setSelectedGender(gender)}
            style={{ marginRight: "8px" }}
          />
          <label htmlFor={gender} style={{ fontSize: "15px" }}>
            {gender}
          </label>
        </div>
      ))}
    </div>
  );
};

export default Gender;
