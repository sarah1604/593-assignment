import cv2
import face_recognition
import os
import pyttsx3
import speech_recognition as sr
from PIL import Image, ImageTk
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the Google Generative AI API key
genai.configure(api_key=" ")

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the recognizer and microphone for speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Initialize GUI components
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sarah's PA - Face Recognition")
        self.geometry("800x600")

        self.video_label = tk.Label(self)
        self.video_label.pack()

        self.chat_window = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.chat_window.pack()

    def update_video(self, img):
        self.video_label.configure(image=img)
        self.video_label.image = img

    def update_chat(self, message):
        self.chat_window.insert(tk.END, message + "\n")
        self.chat_window.yview(tk.END)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech from the microphone
def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

# Function to chat with the Gemini API
def chat_with_gemini(text):
    response = model.generate_content(text)
    return response.text if response.text else "Sorry, I didn't understand that."

# Video capture function to be run in a separate thread
def video_capture_thread(known_face_encodings, gui):
    registered_user_image = None

    # Start video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        gui.update_chat("[ERROR] Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            current_face_locations = face_recognition.face_locations(rgb_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_frame, current_face_locations)

            matches = []
            for encoding in current_face_encodings:
                match = face_recognition.compare_faces(known_face_encodings, encoding)
                if True in match:
                    matches.append(True)

            if any(matches):
                gui.update_chat("Registered user detected. System unlocked.")
                speak("hello sarah, how may i help you")
                # Capture and process speech input
                response = recognize_speech_from_mic(recognizer, microphone)
                if response["transcription"]:
                    gui.update_chat(f"You said: {response['transcription']}")
                    chatbot_response = chat_with_gemini(response['transcription'])
                    gui.update_chat(f"Sarah's PA: {chatbot_response}")
                    speak(chatbot_response)
                else:
                    gui.update_chat(f"Error: {response['error']}")
            else:
                gui.update_chat("Unregistered user detected. Access denied.")

        except Exception as e:
            print(f"Error analyzing frame: {e}")

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        gui.update_video(imgtk)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to load and encode the registered user's images
def load_images_thread(known_face_encodings):
    image_paths = [os.path.join('registered user images', f) for f in os.listdir('registered user images')]
    for image_path in image_paths:
        img = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_face_encodings.append(encoding[0])

# Main function to initialize the GUI and start threads
def main():
    known_face_encodings = []
    gui = GUI()

    # Start the image loading thread
    image_thread = threading.Thread(target=load_images_thread, args=(known_face_encodings,))
    image_thread.start()

    # Wait for images to be loaded before starting video capture
    image_thread.join()

    # Start the video capture thread
    video_thread = threading.Thread(target=video_capture_thread, args=(known_face_encodings, gui))
    video_thread.start()

    # Start the GUI loop
    gui.mainloop()

if __name__ == "__main__":
    main()
