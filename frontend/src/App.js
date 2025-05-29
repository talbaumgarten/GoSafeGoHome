// import React, { useState } from "react";
// import Map from "./Map";

// function App() {
//   const [start, setStart] = useState("");
//   const [end, setEnd] = useState("");
//   const [routeData, setRouteData] = useState(null);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     const response = await fetch("http://localhost:8000/safe-route", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ start, end }),
//     });
//     const data = await response.json();
//     setRouteData(data);
//   };

//   return (
//     <div className="flex flex-col h-screen font-sans">
//       <header className="bg-blue-700 text-white p-4 text-xl font-bold shadow">
//         Safe Route Finder
//       </header>
//       <div className="flex flex-grow">
//         <aside className="w-80 bg-white p-4 shadow-md z-10">
//           <form className="space-y-4" onSubmit={handleSubmit}>
//             <div>
//               <label className="block text-sm font-medium text-gray-700">Start</label>
//               <input
//                 className="w-full p-2 border rounded"
//                 value={start}
//                 onChange={(e) => setStart(e.target.value)}
//               />
//             </div>
//             <div>
//               <label className="block text-sm font-medium text-gray-700">End</label>
//               <input
//                 className="w-full p-2 border rounded"
//                 value={end}
//                 onChange={(e) => setEnd(e.target.value)}
//               />
//             </div>
//             <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
//               Find Safe Route
//             </button>
//           </form>
//           {routeData && (
//             <div className="mt-4 text-sm text-gray-600">
//               <p><strong>Duration: </strong> {routeData["routes"]["duration_minutes"]}</p>
//             </div>
//           )}
//         </aside>
//         <main className="flex-grow relative">
//           <Map route={routeData?.["routes"][0]["geometry"]["coordinates"]} />
//         </main>
//       </div>
//     </div>
//   );
// }

// export default App;


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

  const RouteSummary = ({ route }) => (
    <div className="bg-white p-4 mt-4 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-2">Route Summary</h2>
      <p><strong>From:</strong> {routeData.start_address}</p>
      <p><strong>To:</strong> {routeData.end_address}</p>
      <p><strong>Distance:</strong> {route?.routes?.[0].distance_km.toFixed(2)} km</p>
      <p><strong>Estimated Time:</strong> {route?.routes?.[0].duration_minutes.toFixed(1)} min</p>
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

  const route = routeData; //.routes?.[0];

  return (
    <div className="flex flex-col h-screen font-sans">
      <header className="bg-blue-700 text-white p-4 text-xl font-bold shadow">
        Safe Route Finder
      </header>
      <div className="flex flex-grow">
        <aside className="w-80 bg-gray-50 p-4 shadow-md z-10 overflow-y-auto">
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

          {routeData && route && (
            <>
              <RouteSummary route={route} />
              <StepList steps={route?.routes?.[0].steps} />
            </>
          )}
        </aside>

        <main className="flex-grow relative">
          <Map route={route} /> //.geometry?.coordinates
        </main>
      </div>
    </div>
  );
}

export default App;
