import React, { useState, useEffect, useRef } from "react";
import Map from "./Map";
import mapboxgl from 'mapbox-gl';

// Initialize Mapbox with your token
mapboxgl.accessToken = 'pk.eyJ1Ijoib21lcmRzIiwiYSI6ImNtYjkxd2xhdDBkZmIycXM4ZmRybTk3bjIifQ.EB46ze3YD5Y9nLksQCwN9w'; 

function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [routeData, setRouteData] = useState(null);
  const [startSuggestions, setStartSuggestions] = useState([]);
  const [endSuggestions, setEndSuggestions] = useState([]);
  const [showStartSuggestions, setShowStartSuggestions] = useState(false);
  const [showEndSuggestions, setShowEndSuggestions] = useState(false);
  
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/safe-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start, end }),
      });
      const data = await response.json();
      setRouteData(data);
    } catch (error) {
      console.error("Error fetching route:", error);
      alert("Failed to find route. Please try again.");
    }
  };

  return (
    <div className="flex flex-col h-screen font-sans">
      <header className="bg-blue-700 text-white p-4 text-xl font-bold shadow">
        Safe Route Finder
      </header>
      <div className="flex flex-grow">
        <aside className="w-80 bg-white p-4 shadow-md z-10">
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

            <button 
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors disabled:bg-blue-300"
              disabled={!start || !end}
            >
              Find Safe Route
            </button>
          </form>

          {routeData && (
            <div className="mt-4 p-3 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-800">Route Information</h3>
              <p className="text-sm text-gray-600 mt-1">
                <span className="font-semibold">Safety Score:</span> {routeData.safety_score}
              </p>
              {routeData.distance && (
                <p className="text-sm text-gray-600 mt-1">
                  <span className="font-semibold">Distance:</span> {routeData.distance} miles
                </p>
              )}
              {routeData.duration && (
                <p className="text-sm text-gray-600 mt-1">
                  <span className="font-semibold">Estimated Time:</span> {routeData.duration} mins
                </p>
              )}
            </div>
          )}
        </aside>

        <main className="flex-grow relative">
          <Map route={routeData?.route} />
        </main>
      </div>
    </div>
  );
}

export default App;