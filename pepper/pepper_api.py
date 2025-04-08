import time
import random
from flask import Flask, request, jsonify
import sys
import qi 
from authentication import AuthenticatorFactory

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

# PORT = 9503 # Port for the real robot, always the same 
# PEPPER_IP = "172.20.10.2" # Real robot IP, might change each time there is a connection

"""
app = qi.Application(sys.argv, url="tcps://" + PEPPER_IP + ":" + str(PORT))
logins = ("nao", "vision@2024")
factory = AuthenticatorFactory(*logins)
app.session.setClientAuthenticatorFactory(factory) 
app.start()
"""

if ALProxy:
    print("NAOqi SDK found, using real Pepper")
    tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)  # Speech
    motion = ALProxy("ALMotion", PEPPER_IP, PORT)  # Movement
    leds = ALProxy("ALLeds", PEPPER_IP, PORT)  # LED control 
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
        color = int(0) << 16 | int(255) << 8 | int(0)  # RGB values (0,255,0) for green
        leds.fadeRGB("FaceLeds", color, 0.5) 
        motion.setAngles("HeadPitch", 1, 0.2)
        ## leds.fadeRGB("FaceLeds", int("0000FF", 16), 1.0)
        ## leds.fadeRGB("FaceLeds", 0, 0, 255, 1.0)  # RGB values (0,0,255) for blue
        ## leds.fadeRGB("FaceLeds", 0x0000FF, 1.0)  
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
    print("Moving Pepper to resting position")  # Debugging 
    
    motion.setAngles("RShoulderPitch", 1.8, 0.1)
    motion.setAngles("LShoulderPitch", 1.8, 0.1)
    motion.setAngles("HeadYaw", 0.0, 0.2)
    motion.setAngles("RWristYaw", 0.0, 0.2)  
    motion.setAngles("HeadPitch", 0.0, 0.2)
    motion.setAngles("HipRoll", 0, 0.2)  
    

    return jsonify({"message": "Moving to resting position"})

# Social interaction routes 
@app.route("/get_yes_no", methods=["POST"])
def get_yes_no():
    data = request.get_json()
    input = data.get("input")
    if input == "unclear":
        tts.say("Sorry, I didn't understand. Please say yes or no.")
    else:
        tts.say("Do you want to play a game? Say yes or no.")
    if speech_recognition_found:
        speech_recognition.setLanguage("English")
        speech_recognition.setVocabulary(["yes", "no"], False)
        
        speech_recognition.subscribe("GetYesNo")
        time.sleep(5)  # Wait for Pepper to listen
        speech_recognition.unsubscribe("GetYesNo")

        recognized_answer = memory.getData("WordRecognized")

        if recognized_answer and len(recognized_answer) > 0:
            recognized_word = recognized_answer[0]
            confidence = recognized_answer[1]

            if confidence > 0.4:
                recognized_answer = recognized_word
            else:
                recognized_answer = "unknown"
        else:
            recognized_answer = "unknown"

        if recognized_answer.lower() == "yes":
            tts.say("Great! Let's play!")
            return jsonify({"message": "Yes"})
        elif recognized_answer.lower() == "no":
            tts.say("Alright! Press the button when you want to play!")
            return jsonify({"message": "No"})
        else:
            tts.say("Sorry, I didn't understand. Please say yes or no.")
            return jsonify({"message": "Unclear"})
    else:
        # MOCK FUNCTION
        print("(Mock) Listening for Yes/No...")
        response = random.choice(["yes", "no", "unclear"]) # Simulate responses
        if response == "yes":
            tts.say("Great! Let's play!")
        elif response == "no":
            tts.say("Alright! Press the button when you want to play!")
        return jsonify({"message": response})  
    
@app.route("/get_name", methods=["GET"])
def get_name():
    tts.say("What is your name?")
    if speech_recognition_found:
        speech_recognition.setLanguage("English")
        speech_recognition.setVocabulary([], False)  # Allow any name

        speech_recognition.subscribe("GetName")
        time.sleep(7)  # Wait for Pepper to listen
        speech_recognition.unsubscribe("GetName")

        recognized_name = memory.getData("WordRecognized")

        if recognized_name and len(recognized_name) > 0:
            recognized_word = recognized_name[0]
            confidence = recognized_name[1]

            if confidence > 0.4:
                recognized_name = recognized_word
            else:
                recognized_name = "unknown"
        else:
            recognized_name = "unknown"

        if recognized_name != "unknown":
            tts.say("Nice to meet you, " + recognized_name + "!")
            return jsonify({"message": recognized_name})
        else:
            tts.say("Sorry, I didn't catch that. Please try again.")
            return jsonify({"message": "Unclear"})
    else:
        # MOCK FUNCTION
        print("(Mock) Listening for name...")
        name = random.choice(["Francesca", "unclear"]) # Simulate responses
        if name == "unclear":
            tts.say("Sorry, I didn't catch that. Please try again.")
        else:
            tts.say("Nice to meet you, " + name + "!")
        return jsonify({"message": name})  

@app.route("/greet_user", methods=["GET"])
def greet_user():
    tts.say("Hello! I am Pepper, your friendly robot. Please say hello back when you are ready.")

    if speech_recognition_found:
        speech_recognition.setLanguage("English")
        speech_recognition.setVocabulary(["hi", "hello", "hey"], False)  # Set recognized words

        # Start speech recognition
        speech_recognition.subscribe("SpeechListener")
        print("Pepper is listening for a greeting...")

        while True:
            recognized_answer = memory.getData("WordRecognized")
            if recognized_answer and len(recognized_answer) > 0:
                recognized_word = recognized_answer[0]
                confidence = recognized_answer[1]

                if confidence > 0.4:
                    print("Recognized: {} (Confidence: {})".format(recognized_word, confidence))
                    speech_recognition.unsubscribe("SpeechListener")  # Stop listening
                    return jsonify({"message": recognized_word})  # Return recognized word
                
            time.sleep(1)  # Wait before checking again

    else:
        # MOCK FUNCTION
        print("(Mock) Listening for greeting...")
        return jsonify({"message": random.choice(["hello", "hi", "hey"])})  # Simulate speech recognition

@app.route("/play_again", methods=["GET"])
def play_again():
    tts.say("Do you want to play again? Say yes or no.")
    if speech_recognition_found:
        speech_recognition.setLanguage("English")
        speech_recognition.setVocabulary(["yes", "no"], False)
        
        speech_recognition.subscribe("PlayAgain")
        time.sleep(5)  # Wait for Pepper to listen
        speech_recognition.unsubscribe("PlayAgain")

        recognized_answer = memory.getData("WordRecognized")

        if recognized_answer and len(recognized_answer) > 0:
            recognized_word = recognized_answer[0]
            confidence = recognized_answer[1]

            if confidence > 0.4:
                recognized_answer = recognized_word
            else:
                recognized_answer = "unknown"
        else:
            recognized_answer = "unknown"

        if recognized_answer.lower() == "yes":
            tts.say("Great! It's a rematch")
            return jsonify({"message": "Yes"})
        elif recognized_answer.lower() == "no":
            tts.say("Alright! See you next time")
            return jsonify({"message": "No"})
        else:
            tts.say("Sorry, I didn't understand. Please say yes or no.")
            return jsonify({"message": "Unclear"})
    else:
        # MOCK FUNCTION
        print("(Mock) Listening for Yes/No...")
        response = random.choice(["yes", "no", "unclear"])
        if response == "yes":
            tts.say("Great! It's a rematch")
        elif response == "no":
            tts.say("Alright! See you next time")
        return jsonify({"message": response})  # Simulate responses

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Different port from server.py
