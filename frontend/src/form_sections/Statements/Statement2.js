import React from "react";

const Statement2 = ({ handleLikertSelection, isSelected }) => {

  const descriptions = [
    "Strongly Disagree",
    "",
    "",
    "",
    "Strongly Agree",
  ];

  const likertIcons = [
    "/likert_icons/verysad.png",
    "/likert_icons/sad.png",
    "/likert_icons/neutral.png",
    "/likert_icons/happy.png",
    "/likert_icons/veryhappy.png",
  ];

  const question = {
    id: "sense_of_belonging",
    text: "I feel a sense of belonging in this neighbourhood/place.",
  };

  return (
    <div>
      <p
        style={{
          fontFamily: "Arial, sans-serif",
          fontSize: "16px",
          textAlign: "center",
          margin: "10px 0",
        }}
      >
        {question.text}
      </p>

      <div
        style={{
          display: "flex",
          justifyContent: "space-evenly",
          alignItems: "flex-start",
          width: "100%",
          maxWidth: "400px",
          margin: "0 auto",
          flexWrap: "wrap",
        }}
      >
        {likertIcons.map((icon, index) => {
          const value = index + 1;

          return (
            <button
              key={value}
              onClick={() => handleLikertSelection(question.id, value)}
              aria-label={descriptions[index]}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                flex: 1,
                minWidth: "10px",
                cursor: "pointer",
                background: "none",
                boxShadow: "none",
                border: "none",
                margin: "10px",
              }}
            >
              <img
                src={icon}
                alt={`Likert scale ${value}`}
                style={{
                  width: "35px",
                  height: "35px",
                  display: "block",
                  marginBottom: "5px",
                  border: isSelected === value 
                    ? "3px solid blue" 
                    : "3px solid transparent",
                  borderRadius: "50%",
                  opacity: isSelected === value ? 1 : 0.7,
                  transition: "0.1s ease-in-out",
                }}
              />
              <div
                style={{
                  fontSize: "12px",
                  textAlign: "center",
                  lineHeight: 1,
                  minHeight: "30px",
                  fontWeight: isSelected === value ? "bold" : "normal",
                  fontFamily: "Arial, sans-serif",
                }}
              >
                {descriptions[index]}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default Statement2;
