import React from 'react';
import Slider from 'rc-slider';

const Parameters = ({ parameters, handleCheckboxChange, handleLikertChange }) => {
  return (
    <div>
      <h3>Parameters</h3>
      <p>Choose which of the following parameters makes the location special:</p>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "30px",
          marginBottom: "20px",
        }}
      >
        {parameters.map((param) => (
          <div
            key={param.id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-start",
              gap: "30px",
              width: "50%",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", flex: 1 }}>
              <input
                type="checkbox"
                checked={param.selected}
                onChange={() => handleCheckboxChange(param.id)}
                style={{ marginRight: "10px" }}
              />
              <span>{param.label}</span>
            </div>
            {param.selected && (
              <div style={{ flex: 2 }}>
                <Slider
                  min={1}
                  max={5}
                  marks={{
                    1: "Strongly Disagree",
                    2: "Disagree",
                    3: "Neutral",
                    4: "Agree",
                    5: "Strongly Agree",
                  }}
                  step={null}
                  value={param.value}
                  onChange={(value) => handleLikertChange(param.id, value)}
                  trackStyle={{ backgroundColor: "#4CAF50", height: 6 }}
                  handleStyle={{
                    borderColor: "#4CAF50",
                    height: 16,
                    width: 16,
                    marginTop: 0,
                  }}
                  railStyle={{ backgroundColor: "#ddd", height: 6 }}
                  style={{
                    width: "100%",
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Parameters;
