from flask import Flask, request, jsonify, render_template_string
import requests
import math
import os

app = Flask(__name__)

# Verified Bengaluru Traffic Junctions Database
SMART_JUNCTIONS = [
    {"id": "J1", "name": "Silk Board Junction", "lat": 12.9176, "lng": 77.6235},
    {"id": "J2", "name": "Hebbal Circle", "lat": 13.0355, "lng": 77.5972},
    {"id": "J3", "name": "K.R. Puram Junction", "lat": 13.0035, "lng": 77.6893},
    {"id": "J4", "name": "Mekhri Circle", "lat": 13.0128, "lng": 77.5819},
    {"id": "J5", "name": "Goraguntepalya Junction", "lat": 13.0302, "lng": 77.5458},
    {"id": "J6", "name": "Yeswanthapur Junction", "lat": 13.0245, "lng": 77.5535},
    {"id": "J7", "name": "Domlur Junction", "lat": 12.9612, "lng": 77.6384},
    {"id": "J8", "name": "Trinity Church Junction", "lat": 12.9735, "lng": 77.6183},
    {"id": "J9", "name": "Richmond Circle", "lat": 12.9658, "lng": 77.5962},
    {"id": "J10", "name": "Vellara Junction", "lat": 12.9645, "lng": 77.6055},
    {"id": "J11", "name": "Marathahalli Underpass", "lat": 12.9593, "lng": 77.6976},
    {"id": "J12", "name": "Kundalahalli Gate Junction", "lat": 12.9562, "lng": 77.7013},
    {"id": "J13", "name": "Minerva Circle", "lat": 12.9555, "lng": 77.5770},
    {"id": "J14", "name": "Sirsi Circle", "lat": 12.9563, "lng": 77.5617},
    {"id": "J15", "name": "Nayandahalli Junction", "lat": 12.9475, "lng": 77.5286},
    {"id": "J16", "name": "Mariappa Circle", "lat": 13.0012, "lng": 77.5674},
    {"id": "J17", "name": "Nagavara Junction", "lat": 13.0362, "lng": 77.6152},
    {"id": "J18", "name": "Hope Farm Junction (Whitefield)", "lat": 12.9840, "lng": 77.7522},
    {"id": "J19", "name": "Ananda Rao Circle", "lat": 12.9790, "lng": 77.5728},
    {"id": "J20", "name": "Anil Kumble Circle", "lat": 12.9762, "lng": 77.6032},
    {"id": "J21", "name": "Mysuru Bank Circle", "lat": 12.9778, "lng": 77.5774},
    {"id": "J22", "name": "Kempegowda Circle", "lat": 12.9718, "lng": 77.5796},
    {"id": "J23", "name": "Hudson Circle", "lat": 12.9691, "lng": 77.5896},
    {"id": "J24", "name": "Town Hall Junction", "lat": 12.9651, "lng": 77.5855},
    {"id": "J25", "name": "Shanthala Circle", "lat": 12.9723, "lng": 77.5934},
    {"id": "J26", "name": "Adugodi Junction", "lat": 12.9346, "lng": 77.6103},
    {"id": "J27", "name": "Shoolay Circle", "lat": 12.9612, "lng": 77.6042},
    {"id": "J28", "name": "Lalbagh West Gate Junction", "lat": 12.9484, "lng": 77.5804},
    {"id": "J29", "name": "Konanakunte Cross", "lat": 12.8847, "lng": 77.5788},
    {"id": "J30", "name": "MEI Junction (Tumkur Road)", "lat": 13.0272, "lng": 77.5502},
    {"id": "J31", "name": "Magadi Road Junction", "lat": 12.9682, "lng": 77.5602},
    {"id": "J32", "name": "M.S. Ramaiah Junction", "lat": 13.0322, "lng": 77.5642},
    {"id": "J33", "name": "Modi Hospital Road Junction", "lat": 12.9852, "lng": 77.5532},
    {"id": "J34", "name": "Belathur Gate Junction (SH-35)", "lat": 13.0044, "lng": 77.7572},
    {"id": "J35", "name": "Varthur Kodi Junction", "lat": 12.9482, "lng": 77.7402}
]

# Major Emergency Hospitals Destination Database
HOSPITALS = [
    {"name": "Manipal Hospital, Old Airport Rd", "lat": 12.9581, "lng": 77.6481},
    {"name": "Aster CMI Hospital, Hebbal", "lat": 13.0531, "lng": 77.5906},
    {"name": "St. John's Medical College, Koramangala", "lat": 12.9261, "lng": 77.6231},
    {"name": "Fortis Hospital, Bannerghatta Rd", "lat": 12.8912, "lng": 77.6019},
    {"name": "Narayana Health City, Electronic City", "lat": 12.8236, "lng": 77.6782},
    {"name": "Columbia Asia / Manipal, Yeshwanthpur", "lat": 13.0285, "lng": 77.5492}
]

CLOUD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ambulance Live Tracking & Mapping Dashboard</title>
  <!-- Leaflet CSS for Interactive Map -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body { font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 15px; max-width: 650px; margin: auto; }
    .card { background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 14px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    h2 { color: #38bdf8; margin-top: 0; font-size: 1.15rem; }
    label { font-size: 0.85rem; color: #94a3b8; display: block; margin-bottom: 6px; }
    select, button { width: 100%; border-radius: 8px; font-weight: bold; font-size: 1rem; box-sizing: border-box; }
    select { padding: 10px; background: #0f172a; color: white; border: 1px solid #475569; margin-bottom: 12px; }
    button { background: #059669; color: white; border: none; padding: 14px; cursor: pointer; }
    button:active { background: #047857; }
    .data-box { font-family: monospace; font-size: 0.9rem; line-height: 1.5; color: #a7f3d0; margin-top: 8px; }
    #map { height: 320px; width: 100%; border-radius: 8px; margin-top: 10px; border: 1px solid #475569; z-index: 1; }
    .pulse { display: inline-block; width: 10px; height: 10px; background: #22c55e; border-radius: 50%; animation: pulse 1.5s infinite; margin-right: 6px; }
    @keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.3); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.8; } }
  </style>
</head>
<body>
  <div class="card">
    <h2>🏥 Select Destination Hospital</h2>
    <label for="hospitalSelect">Choose target hospital for emergency routing:</label>
    <select id="hospitalSelect">
      <option value="0">Manipal Hospital, Old Airport Rd</option>
      <option value="1">Aster CMI Hospital, Hebbal</option>
      <option value="2">St. John's Medical College, Koramangala</option>
      <option value="3">Fortis Hospital, Bannerghatta Rd</option>
      <option value="4">Narayana Health City, Electronic City</option>
      <option value="5">Columbia Asia / Manipal, Yeshwanthpur</option>
    </select>
    
    <h2>🚑 Emergency GPS Transmitter</h2>
    <button onclick="startTracking()">START LIVE BROADCAST</button>
    <div id="status" class="data-box" style="margin-top:10px;">Click to authorize location sharing...</div>
  </div>

  <div class="card">
    <h2>🗺️ Live Cloud Route & Map Dashboard</h2>
    <div id="etaOutput" class="data-box">Awaiting active GPS stream...</div>
    
    <!-- Interactive Map Container -->
    <div id="map"></div>
  </div>

  <!-- Leaflet JS Library -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let map = null;
let ambulanceMarker = null;
let hospitalMarker = null;
let routePolyline = null;

function initMap(lat, lng) {
  if (!map) {
    map = L.map('map').setView([lat, lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map);
  }
}

function startTracking() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser");
    return;
  }
  document.getElementById('status').innerText = "Acquiring high-accuracy GPS fix...";
  
  navigator.geolocation.watchPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      const selectedHospitalIdx = document.getElementById('hospitalSelect').value;
      
      document.getElementById('status').innerHTML = `
        <span class="pulse"></span><b>Broadcasting Live GPS:</b><br>
        Lat: ${lat.toFixed(5)} | Lng: ${lng.toFixed(5)}
      `;

      fetch('/api/update_location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: lat, lng: lng, hospital_idx: selectedHospitalIdx })
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('etaOutput').innerHTML = `
          <b>Nearest Traffic Hub:</b> <span style="color:#38bdf8;">${data.closest_junction}</span><br>
          <b>Target Hospital:</b> <span style="color:#f43f5e;">${data.hospital_name}</span><br>
          <b>Straight-line Dist:</b> ${data.straight_dist_m} meters<br><hr>
          <b>🚗 Live Routing Metrics:</b><br>
          • Road Distance: <b>${data.api_distance}</b><br>
          • Dynamic ETA: <span style="color:#facc15; font-size:1.05rem;"><b>${data.api_eta}</b></span>
        `;

        // Initialize or Update Map
        initMap(lat, lng);

        const ambLatLng = [lat, lng];
        const hospLatLng = [data.hospital_lat, data.hospital_lng];

        // Update Ambulance Marker
        if (!ambulanceMarker) {
          ambulanceMarker = L.marker(ambLatLng).addTo(map).bindPopup("<b>🚑 Ambulance Location</b>");
        } else {
          ambulanceMarker.setLatLng(ambLatLng);
        }

        // Update Hospital Marker
        if (!hospitalMarker) {
          hospitalMarker = L.marker(hospLatLng).addTo(map).bindPopup(`<b>🏥 ${data.hospital_name}</b>`);
        } else {
          hospitalMarker.setLatLng(hospLatLng);
          hospitalMarker.bindPopup(`<b>🏥 ${data.hospital_name}</b>`);
        }

        // Draw / Update Route Polyline from OSRM GeoJSON coordinates
        if (data.route_coords && data.route_coords.length > 0) {
          // OSRM returns coordinates as [lng, lat], Leaflet needs [lat, lng]
          const latLngs = data.route_coords.map(coord => [coord[1], coord[0]]);
          
          if (!routePolyline) {
            routePolyline = L.polyline(latLngs, { color: '#2563eb', weight: 5, opacity: 0.8 }).addTo(map);
            map.fitBounds(routePolyline.getBounds(), { padding: [50, 50] });
          } else {
            routePolyline.setLatLngs(latLngs);
          }
        }
      })
      .catch(err => {
        console.error("Cloud sync error:", err);
      });
    },
    (err) => { alert("GPS Error: " + err.message); },
    { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 }
  );
}
</script>
</body>
</html>
"""

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@app.route("/")
def index():
    return render_template_string(CLOUD_HTML)

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.json
    phone_lat = float(data["lat"])
    phone_lng = float(data["lng"])
    h_idx = int(data.get("hospital_idx", 0))
    
    # Get selected hospital
    target_hospital = HOSPITALS[h_idx]
    dest_lat = target_hospital["lat"]
    dest_lng = target_hospital["lng"]

    # Compute closest traffic junction
    closest = min(SMART_JUNCTIONS, key=lambda j: haversine_m(phone_lat, phone_lng, j["lat"], j["lng"]))
    straight_dist = round(haversine_m(phone_lat, phone_lng, closest["lat"], closest["lng"]))
    
    # Query OSRM Route API requesting full geometry coordinates for the Leaflet map polyline
    url = f"http://router.project-osrm.org/route/v1/driving/{phone_lng},{phone_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
    
    api_dist = "N/A"
    api_eta = "N/A"
    route_coords = []
    
    try:
        response = requests.get(url, timeout=5)
        res_data = response.json()
        if res_data.get("code") == "Ok":
            route = res_data["routes"][0]
            dist_m = route["distance"]
            duration_s = route["duration"]
            
            api_dist = f"{dist_m / 1000:.2f} km" if dist_m >= 1000 else f"{dist_m:.0f} m"
            api_eta = f"{max(1, round(duration_s / 60))} mins"
            route_coords = route["geometry"]["coordinates"] # list of [lng, lat]
    except Exception:
        pass

    return jsonify({
        "closest_junction": closest["name"],
        "hospital_name": target_hospital["name"],
        "hospital_lat": dest_lat,
        "hospital_lng": dest_lng,
        "straight_dist_m": straight_dist,
        "api_distance": api_dist,
        "api_eta": api_eta,
        "route_coords": route_coords
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
