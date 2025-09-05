import time
import face_recognition
from haversine import haversine, Unit
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# -----------------------------
# Config
# -----------------------------
DEFAULT_RADIUS_METERS = 100
CLASS_LOCATIONS = {
    "class101": {"lat": 16.794111, "lon": 80.822965},
}

# Load known face
known_image = face_recognition.load_image_file("me.jpg")  # must exist in root
known_encoding = face_recognition.face_encodings(known_image)[0]

# Stability variables
match_start_time = None
verified = False

def verify_location(class_id, user_lat, user_lon):
    class_info = CLASS_LOCATIONS.get(class_id)
    if not class_info:
        raise ValueError(f"Class ID '{class_id}' not found.")

    class_location = (class_info["lat"], class_info["lon"])
    user_location = (user_lat, user_lon)
    distance = haversine(class_location, user_location, unit=Unit.METERS)
    is_in_range = distance <= DEFAULT_RADIUS_METERS
    return is_in_range, distance, class_info


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify():
    global match_start_time, verified

    if "face" not in request.files:
        return jsonify({"error": "No face image uploaded"}), 400

    file = request.files["face"]
    lat = float(request.form.get("lat"))
    lon = float(request.form.get("lon"))

    # Process face
    uploaded_image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(uploaded_image)

    if not encodings:
        match_start_time = None
        verified = False
        return jsonify({"match": False, "status": "No face detected"})

    face_encoding = encodings[0]
    distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
    match = distance < 0.4

    # Stability check
    if match:
        if match_start_time is None:
            match_start_time = time.time()
        elif time.time() - match_start_time >= 5 and not verified:
            verified = True
    else:
        match_start_time = None
        verified = False

    # Location check
    in_range, dist, _ = verify_location("class101", lat, lon) if verified else (False, None, None)

    status = "NO MATCH"
    if match and not verified:
        status = f"MATCH ({distance:.2f}), waiting..."
    elif verified:
        status = f"✅ VERIFIED ({distance:.2f})"

    return jsonify({
        "face_match": match,
        "distance_score": float(distance),
        "verified": verified,
        "status": status,
        "location_verified": in_range,
        "meters_from_class": dist,
        "access": verified and in_range
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
