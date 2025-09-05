FROM python:3.10-slim

# System deps for dlib/face_recognition and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest
COPY . .

# Hugging Face exposes 7860 by default
EXPOSE 7860

# Start Flask
CMD ["python", "app.py"]
