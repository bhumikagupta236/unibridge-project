import cv2
import numpy as np
import base64
import math
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# --- MENTOR NOTE ---
# This file is now much more complex. We are importing:
# - cv2 (OpenCV) and numpy for image processing.
# - base64 to decode the image from the browser.
# - math to calculate distances for finger counting.
# - SocketIO to handle the real-time video stream.
#
# We are *no longer* using 'gTTS', 'os', or 'secure_filename'
# in this specific advanced version, but a full app would
# keep them for the other pages.
# ---

app = Flask(__name__)
# Configure a secret key for SocketIO
app.config['SECRET_KEY'] = 'your_very_secret_key_!@#'
# Wrap our app in SocketIO to enable real-time communication
socketio = SocketIO(app)

# --- Braille Dictionaries ---
# (We keep this logic from our previous lesson)
BRAILLE_DICT = {
    'A': '⠁', 'B': '⠃', 'C': '⠉', 'D': '⠙', 'E': '⠑', 'F': '⠋', 'G': '⠛', 'H': '⠓',
    'I': '⠊', 'J': '⠚', 'K': '⠅', 'L': '⠇', 'M': '⠍', 'N': '⠝', 'O': '⠕', 'P': '⠏',
    'Q': '⠟', 'R': '⠗', 'S': '⠎', 'T': '⠞', 'U': '⠥', 'V': '⠧', 'W': '⠺', 'X': '⠭',
    'Y': '⠽', 'Z': '⠵', ' ': ' ',
    '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
    '6': '⠼_START_IMG_
A hand forming the sign language letter V
_END_IMG_⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚',
}
# Create a reverse dictionary for Braille to Text
TEXT_DICT = {v: k for k, v in BRAILLE_DICT.items()}

# === Standard Page Routes ===

@app.route('/')
def index():
    """Serves the homepage."""
    return render_template('index.html')

@app.route('/speech')
def speech_page():
    """Serves the Speech-to-Text page."""
    return render_template('speech.html')

@app.route('/braille', methods=['GET', 'POST'])
def braille_page():
    """Serves the Braille translator page and handles form submissions."""
    translation = ""
    original_text = ""
    
    if request.method == 'POST':
        if 'text_to_braille' in request.form:
            # --- Text to Braille ---
            text = request.form.get('text', '').upper()
            original_text = text
            braille_translation = [BRAILLE_DICT.get(char, '') for char in text]
            translation = ' '.join(braille_translation)
            
        elif 'braille_to_text' in request.form:
            # --- Braille to Text ---
            braille = request.form.get('braille', '')
            original_text = braille
            # Split by space, as we joined with space
            braille_chars = braille.split(' ')
            text_translation = [TEXT_DICT.get(char, '?') for char in braille_chars]
            translation = ''.join(text_translation)
            
    return render_template('braille.html', translation=translation, original_text=original_text)


@app.route('/learn-sign')
def learn_sign_page():
    """Serves the 'Learn Sign Language' page."""
    return render_template('learn-sign.html')

@app.route('/learn-braille')
def learn_braille_page():
    """Serves the 'Learn Braille' page."""
    return render_template('learn-braille.html')

@app.route('/dictionary')
def dictionary_page():
    """Serves the dictionary page."""
    return render_template('dictionary.html')

@app.route('/sign-to-text')
def sign_page():
    """
    Serves the Sign-to-Text (upload) page.
    NOTE: This route now serves our *live webcam* page.
    """
    return render_template('sign.html')

# === Real-Time Video Processing (SocketIO) ===

def decode_image(data_url):
    """
    Takes a Base64 data URL from the browser and converts it
    into an OpenCV image (numpy array).
    """
    # Split the "data:image/jpeg;base64," prefix from the data
    img_data = data_url.split(',', 1)[1]
    # Decode the Base64 string
    img_bytes = base64.b64decode(img_data)
    # Convert bytes to a numpy array
    np_arr = np.frombuffer(img_bytes, np.uint8)
    # Decode the numpy array into an OpenCV image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def process_frame_opencv(frame):
    """
    Processes a single video frame with OpenCV to count fingers.
    Returns a recognized gesture ('A', 'B', 'C', 'V', 'W') or None.
    """
    # 1. Create a region of interest (ROI) for the hand
    # This is a smaller box where we'll look for the hand
    rows, cols, _ = frame.shape
    # We define a slightly larger ROI to better capture the hand
    roi = frame[50:450, 50:450] # [y:y+h, x:x+w]
    
    # 2. Convert to Grayscale and blur
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (35, 35), 0)

    # 3. Threshold the image
    # This creates a binary (black/white) image of the hand
    _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 4. Find contours (outlines)
    # We're looking for the largest contour, which should be the hand
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None # No contours found

    hand_contour = max(contours, key=cv2.contourArea)
    
    # 5. Check if the contour is reasonably large (to filter noise)
    if cv2.contourArea(hand_contour) < 2500: # Increased size filter
        return None

    # 6. Find the convex hull and convexity defects
    # This is the "magic" for finger counting
    hull = cv2.convexHull(hand_contour, returnPoints=False)
    if len(hull) <= 3:
        return None

    defects = cv2.convexityDefects(hand_contour, hull)
    if defects is None:
        return None

    finger_count = 0
    
    # 7. Loop through the defects to count fingers
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(hand_contour[s][0])
        end = tuple(hand_contour[e][0])
        far = tuple(hand_contour[f][0])

        # Calculate angles of the "triangle" formed by start, end, far
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
        
        # Calculate the angle at the "far" point (the valley between fingers)
        # Use a small epsilon to avoid division by zero
        epsilon = 1e-6
        angle = math.acos((b**2 + c**2 - a**2) / (2*b*c + epsilon)) * 180 / math.pi


        # If the angle is less than 90 degrees, it's a valley
        # and the "far" point is deep enough, count it as a finger
        if angle <= 90 and d > 20: # d is the distance from hull
            finger_count += 1

    # 8. Interpret the finger count
    # finger_count is the number of *valleys*, so add 1 to get fingers
    fingers_visible = finger_count + 1
    
    # --- MENTOR NOTE: New Polished Logic! ---
    
    if fingers_visible >= 4:
        # 4 or 5 fingers = 'B'
        return 'B'
    
    if fingers_visible == 3:
        # 3 fingers = 'W'
        return 'W'
        
    if fingers_visible == 2:
        # 2 fingers = 'V'
        return 'V'
    
    if fingers_visible == 1:
        # This could be 'A' (fist) or 'C' (curved hand)
        # We'll use aspect ratio to tell them apart.
        
        # Calculate the bounding rectangle of the hand
        x, y, w, h = cv2.boundingRect(hand_contour)
        
        # Avoid division by zero
        if h == 0:
            return None 
            
        aspect_ratio = float(w) / h
        
        # 'C' is a wide, curved shape
        if aspect_ratio > 1.25:
            return 'C'
        else:
            # 'A' is a tall/square fist
            return 'A'
    # --- End of New Logic ---
    
    return None # No clear gesture detected

@socketio.on('video_frame')
def handle_video_frame(data):
    """
    This function is called every time the browser 'emits' a
    'video_frame' event. It receives the image data.
    """
    try:
        # 1. Decode the image from the browser
        frame = decode_image(data['image'])
        
        # 2. Process the frame with our OpenCV "brain"
        gesture = process_frame_opencv(frame) # This is our new function
        
        # 3. Send the result back to the browser
        if gesture:
            emit('recognition_result', {'sign': gesture})
        else:
            emit('recognition_result', {'sign': ''}) # Send empty if no gesture

    except Exception as e:
        print(f"Error processing frame: {e}")
        emit('recognition_result', {'sign': '?'})


# === Main execution ===
if __name__ == '__main__':
    # --- MENTOR NOTE ---
    # We now call `socketio.run()` instead of `app.run()`.
    # This starts a server that understands both standard HTTP
    # (for loading pages) and WebSockets (for real-time video).
    print("Starting SocketIO server on http://127.0.0.1:5000")
    socketio.run(app, debug=False, allow_unsafe_werkzeug=False)
