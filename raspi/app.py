from flask import Flask, render_template, Response
import paho.mqtt.client as mqtt
import cv2
 
app = Flask(__name__, static_folder="static")
camera = cv2.VideoCapture(0)

# MQTT settings
# mqtt_server = "192.168.1.241"
mqtt_server = "10.3.141.1"
mqtt_topics = ["arduino/test1", "arduino/test2", "arduino/test3"]
 
last_messages = {topic: "No messages yet" for topic in mqtt_topics}


# MQTT callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code "+str(rc))
    for topic in mqtt_topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    global last_messages
    last_messages[msg.topic] = msg.payload.decode()

def gen_frames():
    while True:
        success, frame = camera.imread()
        if not success:
            break
        else:
            detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
            faces=detector.detectMultiScale(frame,1.1,7)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
             #Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



 
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(mqtt_server, 9001, 60)
 
last_message = "No messages yet"
 
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/data")
def data():
    return render_template("data.html", messages=last_messages)
@app.route("/components")
def components():
    return render_template("components.html")
@app.route("/how-it-works")
def works():
    return render_template("works.html")
@app.route("/getting-started")
def started():
    return render_template("gettingstarted.html")
@app.route("/joystick")
def joystick():
    return render_template("joystick.html")
@app.route("/camera")
def camera():
    return render_template("camera.html")
@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5678, debug=True)
    client.loop_forever()
