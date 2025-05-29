import React, { useState, useEffect, useRef } from "react";
import Map from "./Map";
import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken = 'pk.eyJ1Ijoib21lcmRzIiwiYSI6ImNtYjkxd2xhdDBkZmIycXM4ZmRybTk3bjIifQ.EB46ze3YD5Y9nLksQCwN9w'; 


function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [routeData, setRouteData] = useState(null);
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(0);
  const [startSuggestions, setStartSuggestions] = useState([]);
  const [endSuggestions, setEndSuggestions] = useState([]);
  const [showStartSuggestions, setShowStartSuggestions] = useState(false);
  const [showEndSuggestions, setShowEndSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);


  // Refs for input fields
  const startInputRef = useRef(null);
  const endInputRef = useRef(null);

  // Debounce function to limit API calls
  const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  };

  const fetchSuggestions = async (query, isStart) => {
    if (!query || query.length < 3) {
      isStart ? setStartSuggestions([]) : setEndSuggestions([]);
      return;
    }

    try {
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${mapboxgl.accessToken}&limit=5`
      );
      const data = await response.json();
      const suggestions = data.features.map(feature => ({
        name: feature.place_name,
        center: feature.center
      }));

      if (isStart) {
        setStartSuggestions(suggestions);
      } else {
        setEndSuggestions(suggestions);
      }
    } catch (error) {
      console.error("Error fetching suggestions:", error);
    }
  };

  // Create debounced versions of our fetch function
  const debouncedFetchStartSuggestions = debounce(
    (query) => fetchSuggestions(query, true),
    300
  );
  const debouncedFetchEndSuggestions = debounce(
    (query) => fetchSuggestions(query, false),
    300
  );

  const handleStartChange = (value) => {
    setStart(value);
    debouncedFetchStartSuggestions(value);
    setShowStartSuggestions(true);
  };

  const handleEndChange = (value) => {
    setEnd(value);
    debouncedFetchEndSuggestions(value);
    setShowEndSuggestions(true);
  };

  const selectSuggestion = (suggestion, isStart, e) => {
    e.preventDefault(); // Prevent blur from happening immediately
    if (isStart) {
      setStart(suggestion.name);
      setStartSuggestions([]);
      setShowStartSuggestions(false);
      // Focus back on the input after selection
      setTimeout(() => startInputRef.current?.focus(), 0);
    } else {
      setEnd(suggestion.name);
      setEndSuggestions([]);
      setShowEndSuggestions(false);
      // Focus back on the input after selection
      setTimeout(() => endInputRef.current?.focus(), 0);
    }
  };




  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   const response = await fetch("http://localhost:8000/safe-route", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({ start, end }),
  //   });
  //   const data = await response.json();
  //   setRouteData(data);
  //   setSelectedRouteIndex(0);
  // };
  const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true); // Start loading
  setRouteData(null)
  try {
    const response = await fetch("http://localhost:8000/safe-route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start, end }),
    });
    const data = await response.json();
    setRouteData(data);
  } catch (error) {
    console.error("Failed to fetch route:", error);
  } finally {
    setLoading(false); // Stop loading
  }
};

  const RouteSummary = ({ route }) => (
    <div className="bg-white p-4 mt-4 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-2">Route Summary</h2>
      <p><strong>From:</strong> {routeData.start_address}</p>
      <p><strong>To:</strong> {routeData.end_address}</p>
      <p><strong>Distance:</strong> {routeData?.routes?.[selectedRouteIndex].distance_km.toFixed(2)} km</p>
      <p><strong>Estimated Time:</strong> {routeData?.routes?.[selectedRouteIndex].duration_minutes.toFixed(1)} min</p>
    </div>
  );

  const SafeSummary = ({ route }) => (
    <div className="bg-white p-4 mt-4 rounded-lg shadow">
      <h2 className="text-red-800 font-bold text-lg"><strong>Safety Summary</strong></h2>
      <p className="text-red-800 font-bold"><strong>Safety Rank:</strong> {route.safety_rank}/10</p>
      <p className="text-red-800 font-bold"><strong>Description: </strong> {route.safety_description}</p>
    </div>
  );

  const StepList = ({ steps }) => (
    <div className="bg-white p-4 mt-4 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-2">Directions</h2>
      <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
        {steps.map((step, index) => (
          <li key={index}>
            <p>{step.instruction}</p>
            <p className="text-xs text-gray-500">
              {step.street_name && `via ${step.street_name} • `}
              {Math.round(step.distance_meters)} m • {Math.round(step.duration_seconds / 60)} min
            </p>
          </li>
        ))}
      </ol>
    </div>
  );


  const routes = routeData?.routes || [];


  return (
    <div className="flex flex-col h-screen font-sans">
      <header className="bg-blue-600 text-white p-4 text-xl font-bold shadow">
        SAFETY FIRST
      </header>
      <div className="flex flex-grow">
        <aside className="w-80 bg-gray-50 p-4 shadow-md z-10 overflow-y-auto">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700">Start Location</label>
              <input
                ref={startInputRef}
                className="w-full p-2 border rounded"
                value={start}
                onChange={(e) => handleStartChange(e.target.value)}
                onFocus={() => setShowStartSuggestions(true)}
                onBlur={() => setTimeout(() => setShowStartSuggestions(false), 200)}
                placeholder="Enter starting point"
              />
              {showStartSuggestions && startSuggestions.length > 0 && (
                <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                  {startSuggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-2 hover:bg-gray-100 cursor-pointer"
                      onMouseDown={(e) => selectSuggestion(suggestion, true, e)}
                    >
                      {suggestion.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="relative">
              <label className="block text-sm font-medium text-gray-700">Destination</label>
              <input
                ref={endInputRef}
                className="w-full p-2 border rounded"
                value={end}
                onChange={(e) => handleEndChange(e.target.value)}
                onFocus={() => setShowEndSuggestions(true)}
                onBlur={() => setTimeout(() => setShowEndSuggestions(false), 200)}
                placeholder="Enter destination"
              />
              {showEndSuggestions && endSuggestions.length > 0 && (
                <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                  {endSuggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-2 hover:bg-gray-100 cursor-pointer"
                      onMouseDown={(e) => selectSuggestion(suggestion, false, e)}
                    >
                      {suggestion.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
              Find Safe Route
            </button>
          </form>
          {loading && (
          <div className="mt-4 text-blue-700 font-bold text-center">
            Loading route...
          </div>
        )}

          {routes.length > 0 && (
            <>
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Route:
                </label>
                <select
                  className="w-full p-2 border rounded"
                  value={selectedRouteIndex}
                  onChange={(e) => setSelectedRouteIndex(Number(e.target.value))}
                >
                  {routes.map((r, i) => (
                    <option key={i} value={i}>
                      Route {i + 1} - {r.distance_km.toFixed(1)} km, safe score: {r.safety_rank} 
                    </option>
                  ))}
                </select>
              </div>

              <RouteSummary route={routes[selectedRouteIndex]} />
              <SafeSummary route={routes[selectedRouteIndex]} />
              {/* <StepList steps={routes[selectedRouteIndex].steps} /> */}
            </>
          )}
        </aside>

        <main className="flex-grow relative">
          <Map routeData={routeData} selectedRouteIndex={selectedRouteIndex} />
        </main>
      </div>
    </div>
  );
}

export default App;
