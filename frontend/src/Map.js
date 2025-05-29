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

//     map.addControl(new mapboxgl.NavigationControl());

//     if (route) {
//       // Filter only valid coordinates
//       const coords = route.routes[0].geometry.coordinates.filter(
//         (point) =>
//           Array.isArray(point) &&
//           point.length === 2 &&
//           typeof point[0] === "number" &&
//           typeof point[1] === "number"
//       );

//       map.on("load", () => {
//         // Add route source
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

//         // Add route layer
//         map.addLayer({
//           id: "route",
//           type: "line",
//           source: "route",
//           layout: { "line-cap": "round", "line-join": "round" },
//           paint: { "line-color": "#1D4ED8", "line-width": 5 },
//         });

//         // Add markers at start and end
//         // new mapboxgl.Marker({ color: "green" }).setLngLat(route.start_coordinates).addTo(map);
//         // new mapboxgl.Marker({ color: "red" }).setLngLat(route.end_coordinates).addTo(map);

//         // Fit map to route bounds
//         const bounds = new mapboxgl.LngLatBounds(route.start_coordinates, route.end_coordinates); //coords.reduce((b, coord) => b.extend(coord), 
//         map.fitBounds(bounds, { padding: 5 });
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

const COLORS = ["#1D4ED8", "#10B981", "#F59E0B", "#EF4444", "#6366F1"]; // Blue, Green, Yellow, Red, Indigo

const Map = ({ routeData, selectedRouteIndex }) => {
  const mapRef = useRef();
  const routes = routeData?.routes;

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [34.7800, 32.0750],
      zoom: 13,
    });

    map.addControl(new mapboxgl.NavigationControl());

    map.on("load", () => {
      if (!routes || routes.length == 0) return;

      routes.forEach((route, i) => {
        const coords = route.geometry.coordinates.filter(
          (point) =>
            Array.isArray(point) &&
            point.length === 2 &&
            typeof point[0] === "number" &&
            typeof point[1] === "number"
        );

        const routeId = `route-${i}`;

        map.addSource(routeId, {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "LineString",
              coordinates: coords,
            },
          },
        });

        map.addLayer({
          id: routeId,
          type: "line",
          source: routeId,
          layout: { "line-cap": "round", "line-join": "round" },
          paint: {
            "line-color": COLORS[i % COLORS.length],
            "line-width": i === selectedRouteIndex ? 6 : 3,
            "line-opacity": i === selectedRouteIndex ? 1 : 0.4,
          },
        });
      });

      // const selected = routes[selectedRouteIndex];
      // if (routeData?.start_coordinates && routeData?.end_coordinates) {
        // Add start and end markers
        // new mapboxgl.Marker({ color: "green" }).setLngLat(routeData.start_coordinates).addTo(map);
        // new mapboxgl.Marker({ color: "red" }).setLngLat(routeData.end_coordinates).addTo(map);

        // Fit map to bounds
      const bounds = new mapboxgl.LngLatBounds(
        routeData.start_coordinates,
        routeData.end_coordinates
      );
      map.fitBounds(bounds, { padding: 10 });
      
    });

    return () => map.remove();
  }, [routes, selectedRouteIndex]);

  return <div ref={mapRef} className="absolute inset-0" />;
};

export default Map;
