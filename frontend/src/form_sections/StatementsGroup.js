import React from "react";
import Statement1 from "./Statements/Statement1";
import Statement2 from "./Statements/Statement2";
import Statement3 from "./Statements/Statement3";
import Statement4 from "./Statements/Statement4";
import Statement5 from "./Statements/Statement5";
import Statement6 from "./Statements/Statement6";

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

const StatementsGroup = ({
  groupIndex,
  handleLikertChange,
  handleLikertSelection,
  selectedValues,
}) => {
  const CurrentGroup = statementGroups[groupIndex];

  return (
    <div style={{ padding: "0px 0", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <h3 style={{ marginBottom: "25px", textAlign: "center" }}>Statements</h3>
      {CurrentGroup.map((obj, idx) => {
        const { component: Comp, id: questionId } = obj;
        return (
          <div 
            key={`statement-group-${groupIndex}-${idx}`} 
            style={{ 
              background: "#f5f5f5",
              padding: "10px",
              borderRadius: "10px",
              marginBottom: "14px",
              boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
              width: "500px",
              maxWidth: "90%",
              textAlign: "center",
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
    </div>
  );  
};

export default StatementsGroup;
