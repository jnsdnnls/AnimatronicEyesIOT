from flask import Flask, Response
import cv2
import paho.mqtt.client as mqtt
import json
import logging
import time

app = Flask(__name__)

# MQTT Broker Connection Details
broker_address = '10.3.141.1'
broker_port = 1883
topic = 'joystick/data'

# Initialize the MQTT client
mqtt_client = mqtt.Client()

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
    else:
        logging.error(f"Failed to connect, return code {rc}")

mqtt_client.on_connect = on_connect

try:
    mqtt_client.connect(broker_address, broker_port, 60)
except Exception as e:
    logging.error(f"Connection to MQTT Broker failed: {e}")

# Start the MQTT loop in a separate thread
mqtt_client.loop_start()

# Initialize the video capture
video = cv2.VideoCapture(0)

# Load the Haar cascades for face detection
face_cascade = cv2.CascadeClassifier('C:\\Users\\jensd\\Desktop\\flaskapp\\Haarcascades\\haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return "Default Message"

def gen(video):
    last_sent_time = time.time()
    send_interval = 1.0  # seconds

    while True:
        success, image = video.read()
        if not success:
            break

        # Get the dimensions of the frame
        frame_height, frame_width = image.shape[:2]
        max_x, max_y = 300, 200

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around faces and convert coordinates
        for (x, y, w, h) in faces:
            # Convert to new coordinates system where max coordinates are (200, 0) to (-200, 0)
            new_x = (frame_width // 2 - x) * (max_x / (frame_width // 2))  # Flip x-coordinate
            new_y = (frame_height // 2 - y) * (max_y / (frame_height // 2))

            # Create a dictionary with the coordinates
            coordinates = {'x': new_x, 'y': new_y, 'eyeLids': '511', 'switch': '0'}

            # Convert the dictionary to a JSON string
            json_data = json.dumps(coordinates)

            # Publish face coordinates to MQTT if enough time has passed since the last message
            current_time = time.time()
            if current_time - last_sent_time >= send_interval:
                try:
                    mqtt_client.publish(topic, json_data)
                    logging.info(f"Published: {json_data}")
                    last_sent_time = current_time
                except Exception as e:
                    logging.error(f"Failed to publish MQTT message: {e}")

            cv2.rectangle(image, (x, y), (x + w, y + h), (58, 111, 254), 2)
            cv2.putText(image, f'({new_x}, {new_y})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (58, 111, 254), 2)

        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()

        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True)
