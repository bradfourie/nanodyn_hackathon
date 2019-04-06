import cv2
import os
import numpy as np
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram


TOKEN = "754509199:AAGkdMpcacXSQ7ow4-wZ_fZbDbNaedosFa4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
face_frontal_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
subjects = ["Brad", "Simone"]
lab_access_today = []
group_chat_id = None

face_frontal_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
subjects = ["brad", "Simone"]
lables = {}

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

    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read("trainer.yml")

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
                if( label[0] not in lab_access_today):
                    lab_access_today.append("Brad")
                break
            if ((label[0] == 1) and (label[1] <=90)):
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 50), 2)
                cv2.putText(frame, "Simone", (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                if (label[0] not in lab_access_today):
                    lab_access_today.append("Simone")
                break
            else:
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "INTRUDER", (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                intruder_count = intruder_count + 1
                if group_chat_id != None and intruder_count > 100:
                    cv2.imwrite("intruder.png", face_grey)
                    motion(bot, group_chat_id)
                    intruder_count = 0
                    if(3 not in lab_access_today):
                        lab_access_today.append("Intruder!")

            #cv2.imshow('BRG_face_coord', BRG_face_coord)
                #print(id_)
            #else:
               #frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 50, 255), 2)


    #run for loop for each rectagle in list (note for loop has 4 arguments) ->face_coordinate
        cv2.imshow('frame', frame)
        cv2.waitKey(20)

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
    for i in lab_access_today:
        str += i + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=str)


if __name__ == '__main__':
    main()
