from tensorflow.keras.models import model_from_json
import numpy as np
import cv2
from keras.models import load_model
best_model=load_model('eye.h5')
def FacialExpressionModel(json_file, weights_file):
    with open(json_file,"r") as file:
        loaded_model_json = file.read()
        model = model_from_json(loaded_model_json)

    model.load_weights(weights_file)
    model.compile(optimizer ='adam', loss='categorical_crossentropy', metrics = ['accuracy'])
    return model

facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
model = FacialExpressionModel("model_a.json","model_weights.h5")

def detect_eyes(processed_eye):
    eye_prediction = best_model.predict(processed_eye)
    return eye_prediction

EMOTIONS_LIST = ["Angry","Disgust","Fear","Happy","Neutral","Sad","Surprise"]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = facec.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        cropped_img = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, (48, 48))
        eyes_roi = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(face_roi)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 1)
            eye = eyes_roi[ey:ey + eh, ex:ex + ew]
            processed_eye = cv2.resize(eyes_roi, (224, 224))
            processed_eye = processed_eye / 255.0
            if processed_eye.shape[-1] != 3:
                processed_eye = np.stack((processed_eye,) * 3, axis=-1)
            processed_eye = np.expand_dims(processed_eye, axis=0)
            eye_prediction = detect_eyes(processed_eye)
            if eye_prediction > 0.5:
                eye_status = 'Open'
            else:
                eye_status = 'Closed'
            cv2.putText(frame, f'Eye: {eye_status}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        pred = EMOTIONS_LIST[np.argmax(model.predict(face_roi[np.newaxis,:,:,np.newaxis]))]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, pred, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
