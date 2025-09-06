# Virtual-Mouse-Hand-Recognition-System
This system allows you to control your computer's mouse cursor using hand gestures captured through a webcam. It tracks your hand's movements and specific finger positions to simulate mouse actions like moving, clicking, scrolling, and navigating.

Core Technologies
OpenCV: This library is used to capture video from your webcam, process the image frames, and display visual feedback on the screen.
MediaPipe: Google's MediaPipe framework is the key to hand tracking. It accurately identifies the position of 21 different landmarks on your hand in real-time.
PyAutoGUI: This library performs the actual mouse control actions. Once a gesture is recognized, PyAutoGUI programmatically moves the cursor, performs clicks, or scrolls on the screen.
NumPy: This is used for numerical operations, particularly for calculating distances between hand landmarks.

How It Functions
The system operates in a continuous loop:
Captures Video: It reads the video feed from your webcam frame by frame.
Hand Detection: Each frame is processed by MediaPipe to detect the presence and landmarks of a hand.
Gesture Recognition: The code analyzes the state of the fingers (up or down) and the distances between specific landmarks (like the thumb and index finger) to identify a gesture.
Action Execution: Based on the recognized gesture, PyAutoGUI is instructed to perform a corresponding mouse action.
Visual Feedback: The program overlays information and drawings onto the video feed to show you the detected hand landmarks, the current frames per second (FPS), and the action being performed.


Gesture Controls
The system is designed to respond to the following specific hand gestures:
Activate Mouse Control (✌️): Holding up your index and middle fingers activates the virtual mouse. A "Mouse Control ON" message appears.
Deactivate Mouse Control (🖐️): Holding up all five fingers deactivates mouse control.
Cursor Movement (☝️): When activated, raising only your index finger allows you to move the cursor. The cursor's position on the screen corresponds to the position of your index fingertip in the webcam's view.
Left Click (🤏): Bringing your thumb and index finger close together performs a left-click action.
Right Click: Bringing your index and middle finger tips close together performs a right-click.
Scrolling (👆👇): Holding your index, middle, and ring fingers up activates scroll mode. Moving your hand up scrolls up, and moving it down scrolls down.
Swipe Navigation (⬅️➡️): A quick horizontal movement (swipe) of your index finger to the left simulates pressing Alt + Left Arrow (browser back), and a swipe to the right simulates Alt + Right Arrow (browser forward).
