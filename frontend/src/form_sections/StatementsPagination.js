import React, { useState } from "react";
import Statement1 from "./Statements/Statement1";
import Statement2 from "./Statements/Statement2";
import Statement3 from "./Statements/Statement3";
import Statement4 from "./Statements/Statement4";
import Statement5 from "./Statements/Statement5";
import Statement6 from "./Statements/Statement6";

const StatementsPagination = ({ handleLikertChange, handleLikertSelection, selectedValues }) => {

  const totalGroups = 3;
  const statementGroups = [
    [
      { component: Statement1, id: "personal_connection" },
      { component: Statement2, id: "sense_of_belonging" },
    ],
    [
      { component: Statement3, id: "openness_and_accessibility" },
      { component: Statement4, id: "meet_share_connect" },
    ],
    [
      { component: Statement5, id: "well_designed_for_activities" },
      { component: Statement6, id: "involvement_inspiration" },
    ],
  ];

  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);

  const handleNextGroup = () => {
    if (currentGroupIndex < totalGroups - 1) {
      setCurrentGroupIndex((prev) => prev + 1);
    }
  };

  const handlePreviousGroup = () => {
    if (currentGroupIndex > 0) {
      setCurrentGroupIndex((prev) => prev - 1);
    }
  };

  const CurrentGroup = statementGroups[groupIndex] || [];

  return (
    <div style={{ padding: "0px 0" }}>
      <h3 style={{ marginBottom: "25px", textAlign: "center" }}>Statements</h3>
      {CurrentGroup.map((obj, index) => {
        const { component: Comp, id: questionId } = obj;
  
        return (
          <div
            key={`statement-group-${currentGroupIndex}-${index}`}
            style={{
              background: "#f5f5f5",
              padding: "0px",
              borderRadius: "10px",
              marginBottom: "30px",
              boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
            }}
          >
            <Comp
              handleLikertChange={handleLikertChange}
              handleLikertSelection={handleLikertSelection}
              isSelected={selectedValues[questionId]}
            />
          </div>
        );
      })}

      <div style={{ marginTop: "0px", textAlign: "center" }}>
        {currentGroupIndex > 0 && (
          <button
            onClick={handlePreviousGroup}
            style={{
              marginRight: "12px",
              padding: "10px 18px",
              cursor: "pointer",
              background: "#ddd",
              border: "none",
              borderRadius: "6px",
            }}
          >
            Previous
          </button>
        )}
        {currentGroupIndex < statementGroups.length - 1 ? (
          <button
            onClick={handleNextGroup}
            style={{
              padding: "10px 18px",
              cursor: "pointer",
              background: "#4CAF50",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
            }}
          >
            Next
          </button>
        ) : (
          <p style={{ marginTop: "0px" }}>You have reached the last group of statements.</p>
        )}
      </div>
    </div>
  );
};

export default StatementsPagination;
