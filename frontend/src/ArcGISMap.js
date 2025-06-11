import React, { useEffect, useRef, useState } from "react";
import { loadModules } from "esri-loader";
import axios from "axios";
import "rc-slider/assets/index.css";
import "./ArcGISMap.css";

import { v4 as uuidv4 } from 'uuid';

import Introduction from "./form_sections/Introduction";
import Photo from "./form_sections/Photo";
import StatementsIntro from "./form_sections/StatementsIntro";
import QuestionsIntro from "./form_sections/QuestionsIntro";
import Questions from "./form_sections/Questions";
import StatementsGroup from "./form_sections/StatementsGroup";
import OptInStudy from "./form_sections/OptInStudy";
import Consent from "./form_sections/Consent";
import Age from "./form_sections/Age";
import Gender from "./form_sections/Gender";

const ArcGISMap = () => {
  const mapRef = useRef(null);
  const viewRef = useRef(null);
  const contentRef = useRef(null);

  const [userId, setUserId] = useState(null);
  
  const [pointsLayer, setPointsLayer] = useState(null);
  const [exploreMap, setExploreMap] = useState(false);
  const [isMapMinimized, setIsMapMinimized] = useState(false);
  const [isMapFullscreen, setIsMapFullscreen] = useState(false);
  const [userLocation, setUserLocation] = useState({ latitude: null, longitude: null });
  const [locationError, setLocationError] = useState(null);

  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const [email, setEmail] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState("");
  const [selectedGender, setSelectedGender] = useState("");
  const [isChecked, setIsChecked] = useState(false);

  const [selectedValues, setSelectedValues] = useState({});
  const [freeTextResponses, setFreeTextResponses] = useState({});

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [photoError, setPhotoError] = useState("");

  const resetForm = () => {
    setFormSubmitted(false);
    setCurrentSectionIndex(0);
    setSelectedValues({});
    setFreeTextResponses({});
    setSelectedFile(null);
    setPreviewURL(null);
    setPhotoError("");
    setEmail(null);
    setSelectedAgeGroup("");
    setSelectedGender("");
    setIsChecked(false);
    setSubmitError("");
    setIsMapMinimized(false);
    setExploreMap(false);
  };  

  useEffect(() => {
    if (formSubmitted && mapRef.current) {
      setTimeout(() => {
        window.dispatchEvent(new Event("resize"));
      }, 300);
    }
  }, [formSubmitted]);  

  useEffect(() => {
    function setVH() {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty("--vh", `${vh}px`);
    }

    setVH();

    window.addEventListener("resize", setVH);
    return () => window.removeEventListener("resize", setVH);
  }, []);

  useEffect(() => {
    if (isMapFullscreen && mapRef.current) {
      setTimeout(() => {
        window.dispatchEvent(new Event("resize"));
      }, 300);
    }
  }, [isMapFullscreen]);  

  useEffect(() => {
    let storedId = localStorage.getItem("user_id");
    if (!storedId) {
      storedId = uuidv4();
      localStorage.setItem("user_id", storedId);
    }
    setUserId(storedId);
  }, []);  

  const toggleMapFullscreen = () => {
    setIsMapFullscreen((prev) => !prev);
    setIsMapMinimized(false);
  };

  const handleLikertChange = (questionId, value) => {
    setSelectedValues((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleLikertSelection = (questionId, value) => {
    setSelectedValues((prev) => ({ ...prev, [questionId]: value }));
    handleLikertChange(questionId, value);
  };

  const handleTextChange = (questionId, value) => {
    setFreeTextResponses((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
      if (!allowedTypes.includes(file.type)) {
        setPhotoError("Only JPEG, PNG, and GIF files are allowed.");
        e.target.value = null;
        setSelectedFile(null);
        setPreviewURL(null);
      } else if (file.size > 5 * 1024 * 1024) {
        setPhotoError("File size must be less than 5 MB.");
        e.target.value = null;
        setSelectedFile(null);
        setPreviewURL(null);
      } else {
        setPhotoError("");
        setSelectedFile(file);
        setPreviewURL(URL.createObjectURL(file));
      }
    }
  };

  useEffect(() => {
    let view;
    let pointsLayer;
  
    loadModules(["esri/Map", "esri/views/MapView", "esri/layers/GraphicsLayer"])
      .then(([Map, MapView, GraphicsLayer]) => {
        if (!navigator.geolocation) {
          setLocationError("Geolocation is not supported by this browser.");
          return;
        }
  
        const map = new Map({ basemap: "streets-vector" });
        view = new MapView({
          container: mapRef.current,
          map,
          zoom: 15,
          center: [10.38811452195137, 63.429362470250986],
          popup: {
            dockEnabled: true,
            dockOptions: {
              buttonEnabled: false,
              breakpoint: false,
            },
          },
        });
  
        viewRef.current = view;           
        pointsLayer = new GraphicsLayer();
        map.add(pointsLayer);
        setPointsLayer(pointsLayer);
  
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            setUserLocation({ latitude, longitude });
  
            if (viewRef.current) {
              viewRef.current.goTo({
                center: [longitude, latitude],
                zoom: 15
              }).catch(err => console.error("Error setting map view:", err));
            }
          },
          (error) => {
            console.error("Geolocation error:", error);
            if (error.code === error.PERMISSION_DENIED) {
              setLocationError("Please enable location access to use this map.");
            } else {
              setLocationError("Unable to retrieve your location.");
            }
  
            if (viewRef.current) {
              viewRef.current.goTo({
                center: [10.3881, 63.4293],
                zoom: 12
              });
            }
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
  
      })
      .catch((err) => console.error("Error loading ArcGIS modules:", err));
  
    return () => {
      if (view) view.destroy();
    };
  }, [formSubmitted]);
  

  useEffect(() => {
    if (pointsLayer) {
      fetchLocations();
    }
  }, [pointsLayer]);

  const fetchLocations = async () => {
    function getLikertIconURL(avgLikert) {
      if (!avgLikert) {
        return "/likert_icons/neutral.png";
      }

      if (avgLikert < 1.5) return "/likert_icons/verysad.png";
      if (avgLikert < 2.5) return "/likert_icons/sad.png";
      if (avgLikert < 3.5) return "/likert_icons/neutral.png";
      if (avgLikert < 4.5) return "/likert_icons/happy.png";
      return "/likert_icons/veryhappy.png";
    }

    if (!pointsLayer || !viewRef.current) return;

    try {
      const response = await axios.get(`/api/get-locations`);
      const fetchedLocations = response.data;

      if (!Array.isArray(fetchedLocations)) {
        console.error("Unexpected response format:", fetchedLocations);
        return;
      }

      const [Point, Graphic] = await loadModules(["esri/geometry/Point", "esri/Graphic"]);

      fetchedLocations.forEach((location) => {
        const avgLikertNumber = location.avg_likert ? parseFloat(location.avg_likert) : null;
        const iconURL = getLikertIconURL(avgLikertNumber);

        const point = new Point({
          longitude: location.x_coordinate,
          latitude: location.y_coordinate,
        });

const IMAGE_BASE_URL = "https://csgis.idi.ntnu.no/uploads";

const popupContent = location.image
  ? `<div style="max-width: 300px;">
        <img src="${IMAGE_BASE_URL}/${location.image.split('/').pop()}" 
             alt="Location Photo" 
             style="width: 100%; height: auto; display: block; border-radius: 5px;" />
     </div>`
  : `<p style="font-size: 16px; color: gray; text-align: center;">No photo added for this location</p>`;
      
      const graphic = new Graphic({
        geometry: point,
        symbol: {
          type: "picture-marker",
          url: iconURL,
          width: "32px",
          height: "32px",
        },
        popupTemplate: {
          title: "Location",
          content: popupContent,
          dockEnabled: true,
          dockOptions: {
            buttonEnabled: false,
            breakpoint: false,
          },
        },
      });            

        pointsLayer.add(graphic);
        
      });
    } catch (error) {
      console.error("Error fetching locations:", error);
    }
  };

  const formSections = [
    {
      id: "introduction",
      component: <Introduction />,
    },
    {
      id: "photo",
      component: (
        <Photo
          handleFileChange={handleFileChange}
          photoError={photoError}
          selectedFile={selectedFile}
          previewURL={previewURL}
        />
      ),
    },
    {
      id: "statements_intro",
      component: <StatementsIntro />,
    },
    {
      id: "statements_group_1",
      component: (
        <StatementsGroup
          groupIndex={0}
          handleLikertChange={handleLikertChange}
          handleLikertSelection={handleLikertSelection}
          selectedValues={selectedValues}
        />
      ),
    },
    {
      id: "statements_group_2",
      component: (
        <StatementsGroup
          groupIndex={1}
          handleLikertChange={handleLikertChange}
          handleLikertSelection={handleLikertSelection}
          selectedValues={selectedValues}
        />
      ),
    },
    {
      id: "statements_group_3",
      component: (
        <StatementsGroup
          groupIndex={2}
          handleLikertChange={handleLikertChange}
          handleLikertSelection={handleLikertSelection}
          selectedValues={selectedValues}
        />
      ),
    },
    {
      id: "questions_intro",
      component: <QuestionsIntro />,
    },
    {
      id: "questions",
      component: (
        <Questions
          handleTextChange={handleTextChange}
          freeTextResponses={freeTextResponses}
        />
      ),
    },
    {
      id: "opt_in_consent",
      component: (
        <>
          <Age selectedAgeGroup={selectedAgeGroup} setSelectedAgeGroup={setSelectedAgeGroup} />
          <Gender selectedGender={selectedGender} setSelectedGender={setSelectedGender} />
          <OptInStudy email={email} setEmail={setEmail} />
          <Consent isChecked={isChecked} setIsChecked={setIsChecked} />
        </>
      ),
    },
  ];

  const totalSections = formSections.length - 1;
  const progressPercent = (currentSectionIndex / totalSections) * 100;

  const handleNextSection = () => {
    if (formSections[currentSectionIndex].id === "statements_intro") {
      setIsMapMinimized(true);
    }
  
    if (currentSectionIndex < formSections.length - 1) {
      setCurrentSectionIndex((prevIndex) => prevIndex + 1);
  
      setTimeout(() => {
        if (contentRef.current) {
          contentRef.current.scrollTop = 0;
        }
        
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      }, 10);
    }
  };      

  const handlePreviousSection = () => {
    if (formSections[currentSectionIndex].id === "statements_group_1") {
      setIsMapMinimized(false);
    }
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex((prevIndex) => prevIndex - 1);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isSubmitting) return;

    if (!userLocation.latitude || !userLocation.longitude) {
      setSubmitError("Location data is missing.");
      return;
    }

    if (!isChecked) {
      setSubmitError("Please agree to the data collection consent.");
      return;
    }

    setIsSubmitting(true);

    const parameterResponses = Object.entries(selectedValues).map(([parameter_id, likert_value]) => ({
      parameter_id,
      likert_value,
    }));

    const formattedFreeTextResponses = Object.entries(freeTextResponses).map(([question_id, response]) => ({
      question_id,
      response,
    }));

    const formData = new FormData();
    formData.append("x_coord", userLocation.longitude);
    formData.append("y_coord", userLocation.latitude);
    formData.append("email", email || "");
    formData.append("agreed", isChecked);
    formData.append("age_group_id", selectedAgeGroup);
    formData.append("gender", selectedGender);
    formData.append("parameter_responses", JSON.stringify(parameterResponses));
    formData.append("free_text_responses", JSON.stringify(formattedFreeTextResponses));
    formData.append("user_id", userId);

    if (selectedFile) {
      formData.append("photo", selectedFile);
    }

    try {
      const response = await axios.post(`/api/submit`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.status === 200) {
        await fetchLocations();
        setFormSubmitted(true);
      } else {
        setSubmitError("Failed to submit the form.");
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      setSubmitError("An error occurred while submitting the form.");
    } finally {
      setIsSubmitting(false); // ✅ Done submitting
    }
  };

  let mapHeight;
  if (formSubmitted) {
    mapHeight = "calc(var(--vh) * 80)";
  } else if (isMapFullscreen) {
    mapHeight = "calc(var(--vh) * 100)";
  } else if (isMapMinimized) {
    mapHeight = "calc(var(--vh) * 7)";
  } else {
    mapHeight = "calc(var(--vh) * 80)";
  }  

  const formContainerStyle = isMapFullscreen
    ? { display: "none" }
    : { padding: "0px", marginTop: "10px", marginRight: "20px", marginLeft: "20px", overflowY: "auto" };

  if (locationError) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <h2>Location Access Needed</h2>
        <p>{locationError}</p>
        <p>
          We need your location to show this map and form. Please enable location
          services (or allow the browser prompt) and refresh the page.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh"}}>
      <div
        style={{
          width: "100%",
          height: "6px",
          background: "#ccc",
          position: "fixed",
          top: 0,
          left: 0,
          zIndex: 1000,
        }}
      >
        <div
          style={{
            width: `${progressPercent}%`,
            height: "100%",
            background: "#4CAF50",
            transition: "width 0.3s",
          }}
        />
      </div>
  
      {formSubmitted ? (
exploreMap ? (
  <div className="submittedContainer" style={{ display: "flex", flexDirection: "column"}}>
    <button
      type="button"
      onClick={() => setExploreMap(false)}
      style={{
        backgroundColor: "#4CAF50",
        color: "white",
        border: "none",
        borderRadius: "5px",
        padding: "10px 20px",
        cursor: "pointer",
        position: "absolute",
        top: "10px",
        left: "10px",
        zIndex: 1001,
      }}
    >
      Back to Thanks
    </button>
    <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
  </div>
) : (
<div
  className="submittedContainer"
  style={{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "100vw",
    padding: "0px",
  }}
>
  <div style={{ textAlign: "center", padding: "30px", color: "green", fontSize: "36px", fontWeight: "bold" }}>
    Thanks!
    <p style={{ fontSize: "18px", marginTop: "0px", color: "black" }}>
      Feel free to come back and submit more locations!
    </p>
    <button
      onClick={resetForm}
      style={{
        padding: "10px 20px",
        fontSize: "16px",
        backgroundColor: "#4CAF50",
        color: "white",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
        marginTop: "20px"
      }}
    >
      Make a new submission
    </button>
  </div>

  <div
    ref={mapRef}
    style={{
      flexGrow: 1,
      width: "100%",
      height: "100%",
    }}
  />
</div>
  )
) : (
        <>
          <div
          style={{
            flex: "1 1 auto",
            overflowY: "auto",
            WebkitOverflowScrolling: "touch",
            touchAction: "pan-y",
            paddingTop: "0px",
            paddingBottom: "220px",
          }}
          ref={contentRef}
        >
            <div style={formContainerStyle}>
              {formSections[currentSectionIndex].component}
              <div style={{ marginTop: 0, textAlign: "center" }}>
                {currentSectionIndex > 0 && (
                  <button
                    type="button"
                    style={{
                      marginRight: "20px",
                      padding: "8px 16px",
                      fontSize: "16px",
                      backgroundColor: "#ddd",
                      border: "none",
                      borderRadius: "5px",
                      cursor: "pointer",
                    }}
                    onClick={handlePreviousSection}
                  >
                    Back
                  </button>
                )}
                {currentSectionIndex < formSections.length - 1 ? (
                  <button
                    type="button"
                    style={{
                      padding: "10px 20px",
                      fontSize: "16px",
                      backgroundColor: "#4CAF50",
                      color: "white",
                      border: "none",
                      borderRadius: "5px",
                      cursor: "pointer",
                    }}
                    onClick={() => {
                      handleNextSection();
                      if (contentRef.current) {
                        contentRef.current.scrollTo({ top: 0, behavior: "smooth" });
                      }
                    }}
                  >
                    Next
                  </button>
                ) : (
                  <button
                    type="button"
                    disabled={isSubmitting}
                    style={{
                      padding: "10px 20px",
                      fontSize: "16px",
                      backgroundColor: isSubmitting ? "#999" : "#4CAF50",
                      color: "white",
                      border: "none",
                      borderRadius: "5px",
                      cursor: isSubmitting ? "not-allowed" : "pointer",
                    }}
                    onClick={handleSubmit}
                  >
                    {isSubmitting ? "Submitting..." : "Submit"}
                  </button>
                )}
              </div>
              {currentSectionIndex === formSections.length - 1 && submitError && (
                <p
                  style={{
                    color: "red",
                    fontSize: "14px",
                    textAlign: "center",
                  }}
                >
                  {submitError}
                </p>
              )}
            </div>
          </div>
  
          <div className={isMapFullscreen ? "mapFullscreen" : "mapPinned"}
          style={{ pointerEvents: isMapFullscreen ? "auto" : "none" }}>
            <div
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                zIndex: 999,
              }}
            >
              <button
                type="button"
                onClick={toggleMapFullscreen}
                style={{ cursor: "pointer" }}
              >
                {isMapFullscreen ? "Exit Fullscreen" : "Fullscreen map"}
              </button>
            </div>
            <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
          </div>
        </>
      )}
    </div>
  );   
};

export default ArcGISMap;
