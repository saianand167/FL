# from flask import Flask, request, jsonify, render_template
# import face_recognition
# import numpy as np
# import math
# import base64
# import cv2
# import io
# from PIL import Image

# app = Flask(__name__)

# # -------------------------
# # Reference Face Encoding (replace with your own encoding from training)
# # -------------------------
# REFERENCE_ENCODING = np.array([
#     -0.21994406, 0.08236794, 0.05143112, -0.0571159, 0.02412947, -0.03512193,
#      0.02769779, -0.08322456, 0.18933475, -0.08251249, 0.28062588, -0.02774936,
#     -0.22787049, -0.1260772, 0.05716535, 0.11886792, -0.13367793, -0.11807381,
#     -0.05193415, -0.11017797, 0.07183637, -0.05433441, 0.05328489, 0.12170778,
#     -0.19458061, -0.31278425, -0.12613252, -0.12564665, 0.00877065, -0.12787908,
#     -0.01837935, -0.07100377, -0.2616086, -0.07378796, -0.05732656, 0.08189137,
#     -0.01879851, -0.06106608, 0.17910828, -0.01620582, -0.11978003, -0.06089769,
#     -0.01060433, 0.22059707, 0.13673146, 0.01119261, 0.00294999, -0.01760373,
#      0.00326612, -0.23163997, 0.02685793, 0.09023806, 0.07827414, 0.03871822,
#      0.04746759, -0.18176757, -0.00923449, 0.07679501, -0.15552892, 0.04048435,
#     -0.01607412, -0.06525278, -0.00508338, -0.01092117, 0.26484329, 0.1393155,
#     -0.16776516, -0.09370399, 0.10140089, -0.10721306, 0.05800693, 0.0949785,
#     -0.09453231, -0.22189745, -0.31943911, 0.12229219, 0.44029588, 0.1043664,
#     -0.1926896, -0.01631987, -0.17191915, 0.00238317, 0.05103629, 0.03078607,
#     -0.11182864, 0.05516224, -0.12862118, 0.08031211, 0.14104569, 0.03511178,
#     -0.07943838, 0.17432131, -0.0590466, 0.09033143, 0.04826321, 0.07395397,
#     -0.10314577, -0.01575765, -0.06629934, 0.06494925, 0.01730468, -0.09228993,
#     -0.00803042, 0.10109907, -0.14149156, 0.08871645, 0.03560997, -0.09258564,
#     -0.10160367, 0.09902704, -0.19569722, -0.04178892, 0.09492321, -0.32151833,
#      0.19337125, 0.22194211, -0.02031304, 0.18702291, 0.09087146, 0.06564561,
#     -0.03497, 0.03406234, -0.09005363, -0.01184531, 0.05778141, -0.02403678,
#      0.14184506, 0.00502164
# ])

# # -------------------------
# # Class Location
# # -------------------------
# CLASS_LAT, CLASS_LON = 16.7953564, 80.8234189
# RADIUS = 10000001  # meters

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000
#     dLat = math.radians(lat2 - lat1)
#     dLon = math.radians(lon2 - lon1)
#     a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
#     return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/attendance", methods=["POST"])
# def attendance():
#     data = request.json
#     lat = float(data["lat"])
#     lon = float(data["lon"])
#     image_b64 = data["image"]

#     # ✅ Location check
#     dist = haversine(CLASS_LAT, CLASS_LON, lat, lon)
#     if dist > RADIUS:
#         return jsonify({"success": False, "message": f"❌ Not in class! {dist:.1f}m away"})

#     # ✅ Decode image
#     image_data = base64.b64decode(image_b64.split(",")[1])
#     image = Image.open(io.BytesIO(image_data)).convert("RGB")  # force RGB
#     image = np.array(image)


#     # ✅ Face recognition
#     encodings = face_recognition.face_encodings(image)
#     if not encodings:
#         return jsonify({"success": False, "message": "❌ No face detected!"})

#     face_dist = np.linalg.norm(REFERENCE_ENCODING - encodings[0])
#     if face_dist < 0.42:
#         return jsonify({"success": True, "message": "🎉 Attendance marked!"})
#     else:
#         return jsonify({"success": False, "message": "❌ Face does not match!"})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import geocoder
from haversine import haversine, Unit

# -------------------------
# CLASSROOM LOCATION (example)
# -------------------------
CLASS_LOCATION = (16.7953564, 80.8234189)  # Your classroom coordinates
RADIUS_METERS = 10000000  # Allowed distance

# Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


def check_location():
    g = geocoder.ip("me")
    if g.latlng:
        user_location = tuple(g.latlng)
        distance = haversine(CLASS_LOCATION, user_location, unit=Unit.METERS)
        return distance <= RADIUS_METERS, distance, user_location
    else:
        return False, None, None


def detect_face(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(image_rgb)
        return results.detections if results.detections else []


# -------------------------
# Streamlit UI
# -------------------------
st.title("📸 Face + Location Attendance System")

st.write("This app checks your **face presence** + **location** for attendance.")

# Camera input
img_file = st.camera_input("Take a photo for attendance")

if img_file:
    # Convert to OpenCV image
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    detections = detect_face(image)

    if detections:
        st.success("✅ Face detected!")

        # Check location
        in_range, distance, user_loc = check_location()
        if in_range:
            st.success(f"📍 Location verified (within {RADIUS_METERS}m). Distance: {distance:.2f}m")
            st.balloons()
            st.write("🎉 Attendance marked successfully!")
        else:
            st.error(f"❌ Location not in range. Distance: {distance:.2f}m")
    else:
        st.error("❌ No face detected. Please try again.")
