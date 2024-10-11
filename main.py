# import the necessary libaries to enable chatbot functions 
import cv2 #Used for capturing and processing video from the webcam.
import threading #Allows the chatbot to run the video capture in a separate thread, so it doesn't block other tasks.
import speech_recognition as sr #Captures and processes voice input from the user.
import pyttsx3 # Provides text-to-speech functionality, allowing the bot to speak.
import face_recognition #A library to recognize and compare faces.
import os # Handles file paths and directory operations.
from PIL import Image, ImageTk #Used for image processing.
import tkinter as tk #Creates a simple GUI for the chatbot, including a text area for logs.
from tkinter import scrolledtext

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Directory where registered user's image is stored
USER_IMAGE_DIR = "registered user images"
#REGISTERED_USER_IMAGE = os.path.join(USER_IMAGE_DIR, "user.jpg")

# Load the registered user's face encoding
#registered_user_image = face_recognition.load_image_file(REGISTERED_USER_IMAGE)
registered_user_encoding = [] # an empty list to store face encodings of registered user
for file_name in os.listdir(USER_IMAGE_DIR): # a for loop to go through the pictures of the user in the file directory
    if file_name.startswith("user") and file_name.endswith(".jpg"):
        user_image_path= os.path.join(USER_IMAGE_DIR,file_name)
user_image=face_recognition.load_image_file(user_image_path) # assigning a new variable for face recognition function using the face recognition library to load image
user_encoding=face_recognition.face_encodings(user_image) #assigning a new variable for face recongnition function  using the face recognition library to encode face
[0]
registered_user_encoding.append(user_encoding) # this adds the values from user_encoding variable to the registered_user_encoding list

def speak(text):
    """Function to make the bot speak."""
    engine.say(text)
    engine.runAndWait()

def recognize_face(frame):
    """Function to recognize a face using face_recognition."""
    # Convert the frame from BGR (OpenCV format) to RGB (face_recognition format)
    rgb_frame = frame[:, :, ::-1] # Converts the video frame from BGR (used by OpenCV) to RGB (used by face_recognition).

    # Find all face encodings in the current frame
    face_encodings = face_recognition.face_encodings(rgb_frame) #Extracts face encodings from the current video frame.

    for face_encoding in face_encodings: # for loop to check face and face encodingd to check if they match
        # Compare face encodings with the registered user's encoding
        matches = face_recognition.compare_faces(registered_user_encoding, face_encoding) # Compares the extracted face encodings with the registered user’s encodings. If a match is found, the function returns True.
        if True in matches:
            return True
    return False 
    print("Face detected:", face_encodings)
    print("Matches:", matches)


def take_voice_input():
    """Function to capture voice input from the user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("Sorry, I'm having trouble connecting to the speech service.")
        return None

def video_capture():
    cap = cv2.VideoCapture(0)  # Start video capture from webcam

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    detected_user = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Recognize face
        if recognize_face(frame):
            if not detected_user:
                detected_user = True
                speak("Hello, registered user! How can I assist you?")

                # Take voice input and process it
            user_input = take_voice_input()
            if user_input:
                speak(f"You said: {user_input}")
        else:
            if detected_user:
                detected_user = False
                speak("You are not the registered user.")

        # Display the video frame
        cv2.imshow("Video", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()  # Ensure that the video capture is released properly
    cv2.destroyAllWindows()

def start_bot():
    """Start the chatbot by initializing video capture in a separate thread."""
    video_thread = threading.Thread(target=video_capture)
    video_thread.start()

    # GUI using tkinter for chatbot logs (optional)
def create_gui():
    """Create a simple GUI for chatbot logs."""
    root = tk.Tk()
    root.title("sarah PA") #tweaked

    # Create a scrolled text box for displaying logs
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
    text_area.grid(column=0, row=0, padx=10, pady=10)

    def add_log(log):
        text_area.insert(tk.END, log + '\n')
        text_area.see(tk.END)

         # Start button to run chatbot
    start_button = tk.Button(root, text="Start Chatbot", command=start_bot)
    start_button.grid(column=0, row=1, padx=10, pady=10)

    root.mainloop()

# Run the GUI (optional)









