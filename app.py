from flask import Flask, request, jsonify, render_template_string
import requests
import math
import os

app = Flask(__name__)

# Comprehensive Pan-India / Bengaluru Traffic Junctions Database
SMART_JUNCTIONS = [
    # Major Arterial Intersections & Hubs
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

# Responsive Web Frontend for any browser/mobile device worldwide
CLOUD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Global Ambulance GPS & ETA Tracker</title>
  <style>
    body { font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; max-width: 600px; margin: auto; }
    .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    h2 { color: #38bdf8; margin-top: 0; font-size: 1.25rem; }
    button { background: #059669; color: white; border: none; padding: 14px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; }
    button:active { background: #047857; }
    .data-box { font-family: monospace; font-size: 0.95rem; line-height: 1.6; color: #a7f3d0; margin-top: 10px; }
    .pulse { display: inline-block; width: 10px; height: 10px; background: #22c55e; border-radius: 50%; animation: pulse 1.5s infinite; margin-right: 6px; }
    @keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.3); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.8; } }
  </style>
</head>
<body>
  <div class="card">
    <h2>🚑 Emergency GPS Transmitter</h2>
    <button onclick="startTracking()">START LIVE BROADCAST</button>
    <div id="status" class="data-box" style="margin-top:12px;">Click to authorize location sharing...</div>
  </div>

  <div class="card">
    <h2>🗺️ Live Cloud Command Dashboard</h2>
    <div id="etaOutput" class="data-box">Awaiting active GPS stream...</div>
  </div>

<script>
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
      
      document.getElementById('status').innerHTML = `
        <span class="pulse"></span><b>Broadcasting Live GPS:</b><br>
        Lat: ${lat.toFixed(5)} | Lng: ${lng.toFixed(5)}
      `;

      fetch('/api/update_location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: lat, lng: lng })
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('etaOutput').innerHTML = `
          <b>Nearest Traffic Hub:</b> <span style="color:#38bdf8;">${data.closest_junction}</span><br>
          <b>Straight-line Dist:</b> ${data.straight_dist_m} meters<br><hr>
          <b>🚗 Cloud Route Engine:</b><br>
          • Road Distance: <b>${data.api_distance}</b><br>
          • Dynamic ETA: <span style="color:#facc15; font-size:1.1rem;"><b>${data.api_eta}</b></span>
        `;
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

def get_osrm_route(orig_lat, orig_lng, dest_lat, dest_lng):
    url = f"http://router.project-osrm.org/route/v1/driving/{orig_lng},{orig_lat};{dest_lng},{dest_lat}?overview=false"
    try:
        response = requests.get(url, timeout=4)
        data = response.json()
        if data.get("code") != "Ok":
            return "Routing Error", "Routing Error"
            
        route = data["routes"][0]
        dist_m = route["distance"]
        duration_s = route["duration"]
        
        dist_text = f"{dist_m / 1000:.2f} km" if dist_m >= 1000 else f"{dist_m:.0f} m"
        eta_text = f"{max(1, round(duration_s / 60))} mins"
        return dist_text, eta_text
    except Exception:
        return "Offline Mode", "2 mins"

@app.route("/")
def index():
    return render_template_string(CLOUD_HTML)

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.json
    phone_lat = float(data["lat"])
    phone_lng = float(data["lng"])

    # Compute closest junction
    closest = min(SMART_JUNCTIONS, key=lambda j: haversine_m(phone_lat, phone_lng, j["lat"], j["lng"]))
    straight_dist = round(haversine_m(phone_lat, phone_lng, closest["lat"], closest["lng"]))
    
    # Get live route metrics
    api_dist, api_eta = get_osrm_route(phone_lat, phone_lng, closest["lat"], closest["lng"])

    return jsonify({
        "closest_junction": closest["name"],
        "straight_dist_m": straight_dist,
        "api_distance": api_dist,
        "api_eta": api_eta
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)