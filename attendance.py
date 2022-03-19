import cv2
import numpy as np
import face_recognition
import urllib.request as request
import os
from datetime import datetime
import csv


path = "Images"
images = []
classNames = []
imageList = os.listdir(path)
# print(imageList)

for image_class in imageList:
    currentImg = cv2.imread(f"{path}/{image_class}")
    images.append(currentImg)
    classNames.append(os.path.splitext(image_class)[0])
# print(classNames)


def get_encodings(image_list):
    encode_list = []
    for image in image_list:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
        print(len(encode_list))
    return encode_list


def mark_attendance(person_name):
    with open("Attendance.csv", "r+") as f:
        attendance_list = f.readlines()
        name_list = []
        for line in attendance_list:
            entry = line.split(', ')
            name_list.append(entry[0])
        if person_name not in name_list:
            now = datetime.now()
            time = now.strftime('%H:%M:%S')
            date = now.strftime('%d-%B-%Y')
            f.writelines(f"\n{person_name}, {time}, {date}")


encode_list_for_known_faces = get_encodings(images)
# print("Encoding Complete")

video_capture = cv2.VideoCapture(0)


def show_vid():
    # url = "http://172.20.10.4:8080/shot.jpg"
    # url = "http://213.255.147.195:8080/shot.jpg"
    url = "http://192.168.8.103:8080/shot.jpg"

    while True:
        # capture frame by frame
        # success, img = video_capture.read()
        # if not success:
        #     break

        # if using the phone webcam
        img_resp = request.urlopen(url)
        img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, -1)
        print(img)

        # to resize output
        # width = int(cap.get(3))
        # height = int(cap.get(4))
        # cv2.resize(img, (0, 0), fx=0.5, fx=0.5)

        # resize frame for use
        img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        # cv2.imshow('image_small', img_small)

        face_locations = face_recognition.face_locations(img_small)
        encoded_faces = face_recognition.face_encodings(img_small, face_locations)

        # for encodeFace, faceLoc in zip(encoded_faces, face_locations): # you can use an enumerate here
        for ind, (encodeFace, faceLoc) in enumerate(zip(encoded_faces, face_locations)):
            matches = face_recognition.compare_faces(encode_list_for_known_faces, encodeFace)
            # name = "Unknown"
            name = f"Unknown {ind}"
            face_dist = face_recognition.face_distance(encode_list_for_known_faces, encodeFace)
            # print(face_dist)
            match_index = np.argmin(face_dist)
            print("match_index gotten", match_index)

            # display bounding box and name on image
            if matches[match_index]:
                name = classNames[match_index].upper()
                # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            mark_attendance(name)
            # else:
            #     mark_attendance(name)

        cv2.imshow("video", img)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
