from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

# Home route → serve frontend
@app.route("/")
def home():
    return render_template("index.html")

# API to save attendance
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    username = data.get("name", "Unknown")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append attendance record
    with open("attendance.csv", "a") as f:
        f.write(f"{username},{now}\n")

    return jsonify({"status": "success", "time": now})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
