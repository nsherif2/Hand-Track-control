#Hand Gesture-Controlled System for Volume, Brightness, and Screenshots
This project is a real-time hand gesture recognition system that uses a webcam to track hand movements and control various computer functions such as system volume, screen brightness, minimizing windows, and taking screenshots. The program is built using OpenCV, Mediapipe, and several other libraries for interacting with system audio, screen brightness, and automation tasks.

Features
Hand Gesture Detection:

Detects specific hand gestures such as triangle shapes and fists using Mediapipe.
Tracks both hands simultaneously.
Volume Control:

Adjusts the system volume by recognizing the triangle gesture on the right hand (between the thumb and index finger).
Brightness Control:

Adjusts the screen brightness by recognizing the triangle gesture on the left hand (between the thumb and index finger).
Minimize All Windows:

Detects a squeeze between the thumb and pinky of the left hand to minimize all windows.
User Logout:

Detects both hands in a fist to log the user out of the system.
Screenshot Capture:

Takes a screenshot when both hands form a triangle with their thumbs and index fingers.
Installation
Dependencies
Ensure you have the following libraries installed:

opencv-python
mediapipe
numpy
pycaw
screen-brightness-control
pyautogui
comtypes
You can install these dependencies using the following pip command:

bash
Copy code
pip install opencv-python mediapipe numpy pycaw screen-brightness-control pyautogui comtypes
Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/hand-gesture-control.git
cd hand-gesture-control
Running the Program
After installing the dependencies, you can run the program using:

bash
Copy code
python main.py
How It Works
Webcam Input: The program uses the computer's webcam to capture video frames, which are processed in real-time to detect hand gestures.

Hand Tracking with Mediapipe: The Mediapipe library is used to track hand landmarks and calculate distances between points (fingertips, palm, etc.) to identify gestures.

System Volume Control: By detecting the distance between the thumb and index finger on the right hand, the system volume is adjusted using the pycaw library.

Screen Brightness Control: The screen brightness is adjusted by detecting the triangle gesture on the left hand using the screen-brightness-control library.

Automation with PyAutoGUI: The program minimizes all windows or takes screenshots by sending appropriate keyboard shortcuts via pyautogui.

Logging Out the User: When both hands are detected as fists, the system logs the user out by sending a shutdown command.

Gestures
Volume Control (Right Hand): Form a triangle between your thumb and index finger to adjust the system volume.
Brightness Control (Left Hand): Form a triangle between your thumb and index finger to adjust the screen brightness.
Minimize All Windows: Squeeze the thumb and pinky of your left hand.
User Logout: Close both hands into fists.
Screenshot: Form a triangle by touching your index fingers and thumbs together with both hands.
Known Issues
Make sure that your hand gestures are clear and in good lighting conditions to ensure proper detection.
The screenshot feature has a cooldown of 2 seconds to prevent multiple triggers.
Future Enhancements
Add support for more hand gestures to control other system functions.
Improve gesture recognition accuracy under varying lighting conditions.
Add a GUI to visualize and control the settings of the gesture system.
License
This project is licensed under the MIT License - see the LICENSE file for details.
