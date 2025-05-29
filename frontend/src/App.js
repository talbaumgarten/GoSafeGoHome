import React, { useState } from "react";
import Map from "./Map";

function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [routeData, setRouteData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("http://localhost:8000/safe-route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start, end }),
    });
    const data = await response.json();
    setRouteData(data);
  };

  return (
    <div className="flex flex-col h-screen font-sans">
      <header className="bg-blue-700 text-white p-4 text-xl font-bold shadow">
        Safe Route Finder
      </header>
      <div className="flex flex-grow">
        <aside className="w-80 bg-white p-4 shadow-md z-10">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700">Start</label>
              <input
                className="w-full p-2 border rounded"
                value={start}
                onChange={(e) => setStart(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">End</label>
              <input
                className="w-full p-2 border rounded"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
              />
            </div>
            <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
              Find Safe Route
            </button>
          </form>
          {routeData && (
            <div className="mt-4 text-sm text-gray-600">
              <p><strong>Safety Score:</strong> {routeData.safety_score}</p>
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
