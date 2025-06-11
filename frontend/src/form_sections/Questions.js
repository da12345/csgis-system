import React from "react";

const questionList = [
  { id: "1", text: "Why did you choose this place?" },
  { id: "2", text: "How does this place help to bring people together?" },
  { id: "3", text: "How could this place be improved (with or without technology)?" },
];

const Questions = ({ handleTextChange, freeTextResponses = {} }) => {
  const handleChange = (event, id) => {
    handleTextChange(id, event.target.value);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center"}}>
            <h3 style={{ marginBottom: "25px", textAlign: "center" }}>Questions</h3>
      {questionList.map((q) => (
        <div
          key={q.id}
          style={{
            background: "#f5f5f5",
            padding: "15px",
            borderRadius: "10px",
            marginBottom: "15px",
            boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
            width: "500px",
            maxWidth: "90%",
            textAlign: "center",
          }}
        >
          <p style={{ marginBottom: "7px" }}>{q.text}</p>
          <textarea
            name={`question_${q.id}`}
            placeholder="Please share..."
            rows="1"
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              boxSizing: "border-box",
              display: "block",
            }}
            value={freeTextResponses[q.id] || ""}
onInput={(e) => {
    e.target.style.height = "auto";
    e.target.style.height = `${e.target.scrollHeight}px`;
  }}
            onChange={(e) => handleChange(e, q.id)}
          />
        </div>
      ))}
    </div>
  );
};

export default Questions;
