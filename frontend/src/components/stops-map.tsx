"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { stopsApi, type Stop } from "@/lib/api";

const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function StopsMap() {
  const [stops, setStops] = useState<Stop[]>([]);

  useEffect(() => {
    stopsApi.list().then(setStops).catch(() => setStops([]));
  }, []);

  const center: [number, number] =
    stops.length > 0 ? [stops[0].lat, stops[0].lng] : [40.7128, -74.006];

  return (
    <div style={{ height: 500, width: "100%" }}>
      <MapContainer center={center} zoom={11} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {stops.map((s) => (
          <Marker key={s.id} position={[s.lat, s.lng]} icon={icon}>
            <Popup>
              <strong>{s.name}</strong>
              <br />
              {s.address}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
