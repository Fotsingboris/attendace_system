import numpy as np
import face_recognition
import cv2

def get_face_embedding(image_file):
    """Extracts the face embedding (128D vector) from an image file."""
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    return np.array(encodings[0]) if encodings else None

def verify_face(stored_embedding, image_file, tolerance=0.3):
    """Compares a stored face embedding with a new image."""
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    
    if not encodings:
        return False  # No face found in the image

    # Convert stored embedding back to numpy array
    stored_embedding = np.frombuffer(stored_embedding, dtype=np.float64)

    # Compute face distance (smaller = better match)
    face_distance = face_recognition.face_distance([stored_embedding], encodings[0])[0]

    print(f"Face Distance: {face_distance}")  # Debugging output

    # Return True only if the distance is within the tolerance
    return face_distance < tolerance
