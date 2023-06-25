import streamlit as st
import cv2
from PIL import Image
import numpy as np
from keras.models import model_from_json

# Load pre-trained facial expression recognition model
# (Assuming you have a pre-trained model stored as 'model.h5')
json_file = open('./model/emotion_model1.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

# load weights into new model
model.load_weights("./model/emotion_model1.h5")

# Define class labels for facial expressions
class_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

def detect_expression(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform face detection using a pre-trained cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Process each detected face
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]  # Extract the region of interest (face)

        # Resize face ROI to match the input size of the model
        face_roi = cv2.resize(face_roi, (48, 48))
        face_roi = np.expand_dims(face_roi, axis=0)
        face_roi = np.expand_dims(face_roi, axis=-1)

        # Normalize the face ROI
        face_roi = face_roi / 255.0

        # Predict facial expression using the pre-trained model
        expression_probs = model.predict(face_roi)[0]
        predicted_expression = class_labels[np.argmax(expression_probs)]

        # Draw bounding box and predicted expression label on the image
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, predicted_expression, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return image

def main():
    st.title("Facial Expression Recognition")
    st.write("Choose an option to detect and classify facial expressions.")

    option = st.sidebar.selectbox(
        "Select Input Option",
        ("Built-in Webcam", "External Camera", "Image or Video")
    )

    if option == "Built-in Webcam":
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            st.error("Failed to recognize built-in camera. Please choose other options.")
        else:
            while True:
                ret, frame = video_capture.read()
                frame = detect_expression(frame)
                st.image(frame, channels="BGR", caption="Facial Expression Recognition")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            video_capture.release()
            cv2.destroyAllWindows()

    elif option == "External Camera":
        st.write("External Camera selected")
        # Add your code here to handle external camera input

    elif option == "Image or Video":
        uploaded_file = st.file_uploader("Choose an image or video file", type=["jpg", "jpeg", "png", "mp4"])
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split(".")[-1]
            if file_extension in ["jpg", "jpeg", "png"]:
                image = Image.open(uploaded_file)
                image = np.array(image.convert("RGB"))
                image = detect_expression(image)
                st.image(image, channels="RGB", caption="Processed Image")
            elif file_extension == "mp4":
                st.warning("Video playback is not supported in the current version.")
                # Add your code here to process the video file

if __name__ == "__main__":
    main()
