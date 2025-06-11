import React from "react";

const Age = ({ selectedAgeGroup, setSelectedAgeGroup }) => {
  const ageGroups = ["18-30", "31-45", "46-60", "61-79", "80+"];

  return (
    <div style={{ marginBottom: "30px" }}>
      <h3>Age group</h3>
      {ageGroups.map((age) => (
        <div key={age} style={{ marginBottom: "8px" }}>
          <input
            type="radio"
            id={age}
            name="ageGroup"
            value={age}
            checked={selectedAgeGroup === age}
            onChange={() => setSelectedAgeGroup(age)}
            style={{ marginRight: "8px" }}
          />
          <label htmlFor={age} style={{ fontSize: "15px" }}>
            {age}
          </label>
        </div>
      ))}
    </div>
  );
};

export default Age;
