import numpy as np
import face_recognition
import cv2

def get_face_embedding(image_file):
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    return np.array(encodings[0]) if encodings else None

def verify_face(stored_embedding, image_file):
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    
    if not encodings:
        return False

    return face_recognition.compare_faces([np.frombuffer(stored_embedding)], encodings[0])[0]
