import time
import random
from flask import Flask, request, jsonify
import sys
import qi 
from authentication import AuthenticatorFactory
import math

try:
    from naoqi import ALProxy  # Import the real SDK if available
except ImportError:
    ALProxy = None  # If the SDK isn't installed, use mock functions

app = Flask(__name__)

class MockALProxy:
    """Mock functions for testing without a robot."""
    def __init__(self, service, ip, port):
        self.service = service
        self.ip = ip
        self.port = port

    def say(self, text):
        print("[Mock] Pepper would say: {}".format(text))

    def openHand(self, hand):
        print("[Mock] Pepper would open {}".format(hand))

    def setAngles(self, joint, angle, speed):
        print("[Mock] Pepper would move {} to {} at speed {}".format(joint, angle, speed))

    def fadeRGB(self, led, color, duration):
        print("[Mock] Pepper's {} would fade to {} in {} seconds".format(led, color, duration))

# Initialize Pepper or Mock
PEPPER_IP = "127.0.0.1"  # Virtual robot IP, change when using real robot!!
PORT = 9559  # Change when using real robot!!

#PORT = 9503 # Port for the real robot, always the same 
#PEPPER_IP = "172.20.10.2" # Real robot IP, might change each time there is a connection

"""
app2 = qi.Application(sys.argv, url="tcps://" + PEPPER_IP + ":" + str(PORT))
logins = ("nao", "vision@2024")
factory = AuthenticatorFactory(*logins)
app2.session.setClientAuthenticatorFactory(factory) 
app2.start()
"""

if ALProxy:
    print("NAOqi SDK found, using real Pepper")
    tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)  # Speech
    motion = ALProxy("ALMotion", PEPPER_IP, PORT)  # Movement
    leds = ALProxy("ALLeds", PEPPER_IP, PORT)  # LED control
    """
    tts = app2.session.service("ALTextToSpeech")  # Speech
    motion = app2.session.service("ALMotion")  # Movement
    leds = app2.session.service("ALLeds")  # LED control 
    """
    # animation_player = ALProxy("ALAnimationPlayer", PEPPER_IP, PORT) # Animations from Choregraphe
    try:
        # Try to connect to real speech recognition, when using real robot should go
        speech_recognition = ALProxy("ALSpeechRecognition", PEPPER_IP, PORT)
        speech_recognition.setLanguage("English")
        speech_recognition_found = True
        print("Using real speech recognition.")

    except RuntimeError:
        # If speech recognition is not found, use mock version
        speech_recognition_found = False
        print("ALSpeechRecognition not found! Using mock speech recognition.")
    # memory = ALProxy("ALMemory", PEPPER_IP, PORT) # Memory
else:
    print("!! NAOqi SDK not found, using mock Pepper")
    tts = MockALProxy("ALTextToSpeech", PEPPER_IP, PORT)
    motion = MockALProxy("ALMotion", PEPPER_IP, PORT)
    leds = MockALProxy("ALLeds", PEPPER_IP, PORT)

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        print("Error: Received empty text")
        return jsonify({"error": "Text cannot be empty"}), 400

    # Make text a UTF-8 string 
    text = text.encode("utf-8") if isinstance(text, unicode) else str(text)

    print("Sending text to Pepper: {}".format(repr(text)))  # Debugging
    tts.say(text)  
    return jsonify({"message": "Speaking", "text": text})

@app.route("/announce_turn", methods=["POST"])
def announce_turn():
    data = request.get_json()
    player = data.get("player")
    if player == "X":
        tts.say("It's your turn!")
    else:
        tts.say("It's my turn!")
    return jsonify({"message": "Turn announced", "player": player})

@app.route("/announce_winner", methods=["POST"])
def announce_winner():
    data = request.get_json()
    winner = data.get("winner")
    
    if winner == "O":
        tts.say("I won! Good game!")
        leds.fadeRGB("FaceLeds", "green", 1) 
        motion.angleInterpolation("HipRoll", math.radians(-30), 1, True)
        motion.angleInterpolation("HipRoll", math.radians(30), 1, True)
        motion.angleInterpolation("HipRoll", math.radians(-30), 1, True)
        motion.angleInterpolation("HipRoll", math.radians(30), 1, True)
    elif winner == "X":
        tts.say("You won! Well played!")
        color = int(0) << 16 | int(255) << 8 | int(0)  # RGB values (0,255,0) for green
        leds.fadeRGB("FaceLeds", "blue", 1) 
        motion.angleInterpolation("HeadPitch", math.radians(30), 1, True)
    elif winner == "draw":
        tts.say("It's a draw!")
        leds.fadeRGB("FaceLeds", "yellow", 1)
        motion.angleInterpolation("HeadYaw", math.radians(-30), 1, True)
        motion.angleInterpolation("HeadPitch", math.radians(9), 1, True)
        motion.angleInterpolation("HipRoll", math.radians(-28), 1, True)

    return jsonify({"message": "Winner announced", "winner": winner})

@app.route("/resting_position", methods=["POST"])
def resting_position():
    print("Moving Pepper to resting position")  # Debugging 
    motion.angleInterpolation("HeadYaw", math.radians(0), 0.5, True)
    motion.angleInterpolation("HeadPitch", math.radians(0), 0.5, True)
    motion.angleInterpolation("HipRoll", math.radians(0), 0.5, True)
    return jsonify({"message": "Moving to resting position"})

# Social interaction routes moved to server.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Different port from server.py
