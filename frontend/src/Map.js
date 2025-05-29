// import React, { useEffect, useRef } from "react";
// import mapboxgl from "mapbox-gl";

// mapboxgl.accessToken = "pk.eyJ1Ijoib21lcmRzIiwiYSI6ImNtYjkxd2xhdDBkZmIycXM4ZmRybTk3bjIifQ.EB46ze3YD5Y9nLksQCwN9w";

// const Map = ({ route }) => {
//   const mapRef = useRef();

//   useEffect(() => {
//     const map = new mapboxgl.Map({
//       container: mapRef.current,
//       style: "mapbox://styles/mapbox/streets-v11",
//       center: [34.7818, 32.0853],
//       zoom: 13,
//     });

//     if (route) {
//       const coords = route.map((point) => [point.lng, point.lat]);
//       map.on("load", () => {
//         map.addSource("route", {
//           type: "geojson",
//           data: {
//             type: "Feature",
//             geometry: {
//               type: "LineString",
//               coordinates: coords,
//             },
//           },
//         });

//         map.addLayer({
//           id: "route",
//           type: "line",
//           source: "route",
//           layout: { "line-cap": "round", "line-join": "round" },
//           paint: { "line-color": "#1D4ED8", "line-width": 5 },
//         });

//         coords.forEach((coord) => {
//           new mapboxgl.Marker().setLngLat(coord).addTo(map);
//         });
//       });
//     }

//     return () => map.remove();
//   }, [route]);

//   return <div ref={mapRef} className="absolute inset-0" />;
// };

// export default Map;


import React, { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = "pk.eyJ1Ijoib21lcmRzIiwiYSI6ImNtYjkxd2xhdDBkZmIycXM4ZmRybTk3bjIifQ.EB46ze3YD5Y9nLksQCwN9w";

const Map = ({ route }) => {
  const mapRef = useRef();

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [34.7818, 32.0853],
      zoom: 13,
    });

    map.addControl(new mapboxgl.NavigationControl());

    if (route) {
      // Filter only valid coordinates
      const coords = route.routes[0].geometry.coordinates.filter(
        (point) =>
          Array.isArray(point) &&
          point.length === 2 &&
          typeof point[0] === "number" &&
          typeof point[1] === "number"
      );

      map.on("load", () => {
        // Add route source
        map.addSource("route", {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "LineString",
              coordinates: coords,
            },
          },
        });

        // Add route layer
        map.addLayer({
          id: "route",
          type: "line",
          source: "route",
          layout: { "line-cap": "round", "line-join": "round" },
          paint: { "line-color": "#1D4ED8", "line-width": 5 },
        });

        // Add markers at start and end
        // new mapboxgl.Marker({ color: "green" }).setLngLat(route.start_coordinates).addTo(map);
        // new mapboxgl.Marker({ color: "red" }).setLngLat(route.end_coordinates).addTo(map);

        // Fit map to route bounds
        const bounds = coords.reduce((b, coord) => b.extend(coord), new mapboxgl.LngLatBounds(coords[0], coords[0]));
        map.fitBounds(bounds, { padding: 50 });
      });
    }

    return () => map.remove();
  }, [route]);

  return <div ref={mapRef} className="absolute inset-0" />;
};

export default Map;
