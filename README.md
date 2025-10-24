🌟 UniBridge - Universal Communication & Learning Platform

UniBridge is a full-stack web application designed to break down communication barriers. It provides tools and learning modules for Sign Language, Braille, and Speech, all in one accessible, web-based platform.

This project was built from scratch as a beginner-friendly introduction to full-stack development, real-time communication, and computer vision.

<!-- You can add one of your screenshots here! -->

<!--  -->

✨ Core Features

This platform combines multiple communication and learning tools into a single, cohesive interface.

Speech ↔ Text: Uses the browser's Web Speech API for real-time speech recognition (Speech-to-Text) and speech synthesis (Text-to-Speech).

Braille ↔ Text: A full-stack translator that converts text to Braille and vice-versa using a Python backend.

Live Sign Recognition (A-W): Uses OpenCV, NumPy, and Socket.IO to stream a live webcam feed to the Python server, analyze the hand's shape in real-time, and recognize 5 different signs (A, B, C, V, W).

Learn Sign Language: An interactive, flashcard-style e-learning module that dynamically loads lessons from a JSON data file.

Learn Braille: A similar e-learning module for learning the Braille alphabet, also driven by a JSON file.

Universal Dictionary: A searchable, live-filtering dictionary that loads data from a JSON file and displays words in multiple formats (text, Braille, sign image, and audio).

Fully Accessible: Built with accessibility in mind, featuring keyboard navigation (focus:ring), aria-labels for screen readers, and a high-contrast, large-font design.

🛠️ Tech Stack

Backend

Python 3

Flask: The core web server and routing.

Flask-SocketIO: For real-time, bidirectional communication (for the webcam stream).

OpenCV-Python: For all computer vision tasks (frame processing, contour detection, shape analysis).

NumPy: For high-performance numerical operations on video frames.

Gunicorn & Eventlet: Production-ready WSGI server setup for deploying SocketIO.

Frontend

HTML5: Structured and semantic markup.

Tailwind CSS: For all styling, components, and responsive design.

JavaScript (ES6+): For interactivity, DOM manipulation, and API calls.

Web Speech API: Browser-native API for speech recognition and synthesis.

Socket.IO Client: The JavaScript "half" that connects to the Python server for real-time streaming.

Lucide Icons: For clean, modern vector icons.

🚀 How to Run Locally

Follow these steps to get a local copy of the project up and running.

Prerequisites:

Python 3.8+

pip (Python package installer)

1. Clone the Repository:

git clone [https://github.com/YOUR_USERNAME/unibridge-project.git](https://github.com/YOUR_USERNAME/unibridge-project.git)
cd unibridge-project


2. Create and Activate a Virtual Environment:

This creates a clean "project box" for your libraries.

# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate


3. Install Requirements:

This installs all the Python libraries listed in the requirements.txt file.

pip install -r requirements.txt


4. Run the Application:

python uni.py


5. Open Your Browser:

Navigate to http://127.0.0.1:5000 to see the application live!

📁 Project Structure

unibridge/
├── .gitignore          # Tells Git what to ignore (like venv)
├── README.md           # You are here!
├── requirements.txt    # The "shopping list" of Python libraries
├── uni.py              # The main Flask "brain" (server, all logic)
│
├── templates/          # All HTML files
│   ├── index.html
│   ├── speech.html
│   ├── braille.html
│   ├── sign.html
│   ├── learn-sign.html
│   ├── learn-braille.html
│   └── dictionary.html
│
├── static/
│   ├── data/           # Our JSON "databases"
│   │   ├── sign_lessons.json
│   │   ├── braille_lessons.json
│   │   └── dictionary.json
│   └── (Other assets like CSS or images would go here)
│
└── venv/               # (Your local virtual environment)
