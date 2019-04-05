import cv2
import os
import numpy as np
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram


TOKEN = "754509199:AAGkdMpcacXSQ7ow4-wZ_fZbDbNaedosFa4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
face_frontal_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
subjects = ["Brad", "Simone"]
group_chat_id = None

def main():
    bot = telegram.Bot(token='754509199:AAGkdMpcacXSQ7ow4-wZ_fZbDbNaedosFa4')
    updater = Updater('754509199:AAGkdMpcacXSQ7ow4-wZ_fZbDbNaedosFa4')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('motion', motion))
    dp.add_handler(CommandHandler('verified', verified))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
   # updater.idle()

    intruder_count = 0

    print(bot)

    print("no man")

    faces, labels = prep_train("Portrait_database")
    print ("total faces:", len(faces))
    print("total labels:", len(labels))

    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(faces, np.array(labels))

    cap = cv2.VideoCapture(0)
    while(True):

        ret, frame = cap.read()
        frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_coordinate = face_frontal_cascade.detectMultiScale(frame_grey, scaleFactor=1.1, minNeighbors=5)

        for x,y,w,h in face_coordinate:
            face_grey = frame_grey[ y:y + h, x: x + w]
            label = face_recognizer.predict(face_grey)

            if ((label[0] == 0) and (label[1] <=90)):
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 50), 2)
                cv2.putText(frame, "Brad", (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                break
            if ((label[0] == 1) and (label[1] <=90)):
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 50), 2)
                cv2.putText(frame, "Simone", (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                break
            else:
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "INTRUDER", (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                intruder_count = intruder_count + 1
                if group_chat_id != None and intruder_count > 50:
                    cv2.imwrite("intruder.png", face_grey)
                    motion(bot, group_chat_id)
                    intruder_count = 0

            #cv2.imshow('BRG_face_coord', BRG_face_coord)
                #print(id_)
            #else:
               #frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 50, 255), 2)


    #run for loop for each rectagle in list (note for loop has 4 arguments) ->face_coordinate
        cv2.imshow('frame', frame)
        cv2.waitKey(20)

def detect_face(image):
    frame_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_frontal_cascade.detectMultiScale(frame_grey, scaleFactor=1.1, minNeighbors=5)
    print(len(faces))
    if (len(faces) == 0):
        return None, None
    (x, y, w, h) = faces[0]
    return frame_grey[y:y + h, x: x + w], faces[0]

def prep_train (data_folder_path):
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
                print(id_)


                if face is not None:
                    faces.append(face)
                    label.append(id_)


    return faces, label


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Invalid input message")

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You have now registered for updates from the CCTV Camera!")
    gc_id = update.message.chat_id
    global group_chat_id
    group_chat_id = gc_id
    print(group_chat_id)

def motion(bot, update):
    url = "https://nu.aeon.co/images/fb911487-7bbe-4752-b655-3c8b0d745801/idea_sized-bigfoot_gimli_patterson.jpg"
    bot.send_photo(chat_id=update.message.chat_id, photo=url)
    bot.send_message(chat_id=update.message.chat_id, text="Unauthorised motion has been detected")

def motion(bot, chat_id):
    bot.send_photo(chat_id=chat_id, photo=open('intruder.png', 'rb'))
    bot.send_message(chat_id=chat_id, text="Unauthorised motion has been detected")

def verified(bot, update):
    str = "Users with access to lab:\n"
    for i in subjects:
        str += i + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=str)

def report(bot, update):
    str = "Users seen in the lab today:\n"
    for i in subjects:
        str += i + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=str)


if __name__ == '__main__':
    main()
