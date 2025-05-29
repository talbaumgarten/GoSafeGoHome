import React, { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = "pk.eyJ1Ijoib21lcmRzIiwiYSI6ImNtYjkxd2xhdDBkZmIycXM4ZmRybTk3bjIifQ.EB46ze3YD5Y9nLksQCwN9w";

const Map = ({ route }) => {
  const mapRef = useRef();

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [-73.985428, 40.748817],
      zoom: 13,
    });

    if (route) {
      const coords = route.map((point) => [point.lng, point.lat]);
      map.on("load", () => {
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

        map.addLayer({
          id: "route",
          type: "line",
          source: "route",
          layout: { "line-cap": "round", "line-join": "round" },
          paint: { "line-color": "#1D4ED8", "line-width": 5 },
        });

        coords.forEach((coord) => {
          new mapboxgl.Marker().setLngLat(coord).addTo(map);
        });
      });
    }

    return () => map.remove();
  }, [route]);

  return <div ref={mapRef} className="absolute inset-0" />;
};

export default Map;
