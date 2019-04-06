import cv2
import os
import pickle
import numpy as np
face_frontal_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

def detect_face(image):
    frame_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_frontal_cascade.detectMultiScale(frame_grey, scaleFactor=1.1, minNeighbors=5)
    print(len(faces))
    if (len(faces) == 0):
        return None, None
    (x, y, w, h) = faces[0]
    return frame_grey[y:y + h, x: x + w], faces[0]

def main ():
    data_folder_path = "Portrait_database"
    base_directory = os.path.dirname(os.path.abspath(__file__))
    image_directory = os.path.join(base_directory, data_folder_path)
    curr_id = 0
    label_ids = {}
    faces = []
    label = []

    for root, dirs, files in os.walk(image_directory):
        for file in files:
            if file.endswith("jpeg") or ("jpg"):
                path = os.path.join(root, file)
                name = os.path.basename(os.path.dirname(path)).replace(" ", "_").lower()
                if not name in label_ids:
                    label_ids[name] = curr_id
                    curr_id += 1
                id_ = label_ids[name]

                img_temp = cv2.imread(path)
                img = cv2.resize(img_temp, (360, 480))
                face, rect = detect_face(img)

                if face is not None:
                    faces.append(face)
                    label.append(id_)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    with open("labels.pkl", 'wb') as f:
        pickle.dump(label_ids, f)

    recognizer.train(faces, np.array(label))
    recognizer.save("trainer.yml")

    print("recog - done")
    print(recognizer)

    #return faces, label

if __name__ == '__main__':
    main()