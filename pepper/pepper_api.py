import time
from flask import Flask, request, jsonify

try:
    from naoqi import ALProxy  # Import the real SDK if available
except ImportError:
    ALProxy = None  # If the SDK isn't installed, use mock functions

app = Flask(__name__)

class MockALProxy:
    """Mock version of NAOqi's ALProxy for testing without a robot."""
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
PEPPER_IP = "127.0.0.1"  # Virtual robot IP
PORT = 9559

if ALProxy:
    print("NAOqi SDK found, using real Pepper")
    tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)  # Speech
    motion = ALProxy("ALMotion", PEPPER_IP, PORT)  # Movement
    leds = ALProxy("ALLeds", PEPPER_IP, PORT)  # LED control
    animation_player = ALProxy("ALAnimationPlayer", PEPPER_IP, PORT) # Animations from Choregraphe
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

    # Ensure text is a clean UTF-8 string
    text = text.encode("utf-8") if isinstance(text, unicode) else str(text)

    print("Sending text to Pepper: {}".format(repr(text)))  # Debugging log
    tts.say(text)  # Make Pepper speak
    return jsonify({"message": "Speaking", "text": text})

@app.route("/announce_turn", methods=["POST"])
def announce_turn():
    data = request.get_json()
    player = data.get("player")
    if player == "X":
        tts.say("It's your turn!")
    else:
        tts.say("Let me think...")
    return jsonify({"message": "Turn announced", "player": player})

@app.route("/announce_winner", methods=["POST"])
def announce_winner():
    data = request.get_json()
    winner = data.get("winner")
    
    if winner == "O":
        tts.say("I won! Good game!")
        motion.openHand("LHand")
        motion.openHand("RHand")
        motion.setAngles("HipRoll", 5 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", 0 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", -5 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", 0 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", 5 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", 0 , 0.1)
        time.sleep(2)
        motion.setAngles("HipRoll", -5 , 0.1)
    elif winner == "X":
        tts.say("You won! Well played!")
        leds.fadeRGB("FaceLeds", "blue", 0.5) 
        motion.setAngles("HeadPitch", 1, 0.2)
        ## leds.fadeRGB("FaceLeds", int("0000FF", 16), 1.0)
        ## leds.fadeRGB("FaceLeds", 0, 0, 255, 1.0)  # Explicit RGB values (0,0,255) for blue
        ## leds.fadeRGB("FaceLeds", 0x0000FF, 1.0)  # Blue face
    else:
        tts.say("It's a draw!")
        motion.setAngles("HeadYaw", 0.3, 0.2)
        motion.setAngles("HeadYaw", -0.6, 0.2)
        motion.setAngles("HeadPitch", 0.0, 0.2)
        motion.setAngles("HipRoll", 2.5, 0.2)
        motion.setAngles("HipRoll", -5, 0.2)

    return jsonify({"message": "Winner announced", "winner": winner})

@app.route("/resting_position", methods=["POST"])
def resting_position():
    print("Moving Pepper to resting position")  # Debugging print
    
    motion.setAngles("RShoulderPitch", 1.8, 0.1)
    motion.setAngles("LShoulderPitch", 1.8, 0.1)
    motion.setAngles("HeadYaw", 0.0, 0.2)
    motion.setAngles("RWristYaw", 0.0, 0.2)  
    motion.setAngles("HeadPitch", 0.0, 0.2)
    motion.setAngles("HipRoll", 0, 0.2)  
    

    return jsonify({"message": "Moving to resting position"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Different port from server.py
