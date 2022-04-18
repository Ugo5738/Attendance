import cv2
import numpy as np
import face_recognition
import urllib.request as request
import os
from datetime import datetime
from calendar import Calendar
import csv


# path = "Attendance/Images_upload/"
path = "Images_upload/"
images = []
classNames = []
imageList = os.listdir(path)
# print(imageList)


Calendar = Calendar()
today = datetime.now()

YEAR = today.year
MONTH = today.month
WED_START_TIME = 16
WED_STOP_TIME = 21
SUN_START_TIME = 6
SUN_STOP_TIME = 17
os.environ.get("SPECIAL_PROGRAM_START_TIME", 16)
os.environ.get("SPECIAL_PROGRAM_STOP_TIME", 21)
FILE_NAME = 'Attendance.csv'

now = datetime.now()
time = now.strftime('%H:%M:%S')
date = now.strftime('%d-%B-%Y')
day = now.strftime('%A')
os.environ["SPECIAL_DAY"] = ''

for image_class in imageList:
    currentImg = cv2.imread(f"{path}/{image_class}")
    images.append(currentImg)
    classNames.append(os.path.splitext(image_class)[0])
# print(classNames)


def get_encodings(image_list):
    encode_list = []
    for ind, image in enumerate(image_list):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
    return encode_list


class MarkAttendance:
    def __init__(self, file_name, time_, date_, day_):
        self.file_name = file_name
        # self.person_name = person_name
        self.time = time_
        self.date = date_
        self.day = day_

    def exist_attendance(self, person_name):
        with open(self.file_name, 'r+') as file:
            name_list = []  # this could be put in a txt document
            content = file.readlines()
            header = content[:1]
            rows = content[1:]
            for entry in rows:
                entry = entry.split(", ")
                entry[-1] = entry[-1].split()[0]  # not sure that this line is needed
                full_name = f'{entry[0]} {entry[1]} {entry[2]}'
                name_list.append(full_name)
            if person_name not in name_list:
                new_member = person_name.split()
                first_name = new_member[0]
                middle_name = new_member[1]
                last_name = new_member[2]
                file.writelines(f"\n{first_name}, {middle_name}, {last_name}, {self.time}, {self.date}, {self.day}")

    def new_attendance(self, person_name):
        first_person = person_name.split()
        first_name = first_person[0]
        middle_name = first_person[1]
        last_name = first_person[2]
        attendance_file = open(self.file_name, 'w')
        attendance_file.write(f"First Name, Middle Name, Last Name, Time In, Date, Day")
        # mark attendance
        attendance_file.write(f"\n{first_name}, {middle_name}, {last_name}, {time}, {date}, {day}")
        attendance_file.close()

    def mark_present(self, person_name):
        if os.path.isfile(self.file_name):
            mark_attendance.exist_attendance(person_name=person_name)
        else:
            mark_attendance.new_attendance(person_name=person_name)


def attendance_db():
    with open('Attendance.csv') as file:
        content = file.readlines()
        header = content[:1]
        rows = content[1:]
        row_list = []
        for row in rows:
            row = row.split(", ")
            row[-1] = row[-1].split()[0]
            row_list.append(row)
        return row_list


mark_attendance = MarkAttendance(file_name=FILE_NAME, time_=time, date_=date, day_=day)

encode_list_for_known_faces = get_encodings(images)
# print("Encoding Complete")

# video_capture = cv2.VideoCapture(0)


START = False

if day == "Wednesday":
    if today.hour in range(WED_START_TIME, WED_STOP_TIME+1):
        START = True
elif day == "Sunday":
    if today.hour in range(SUN_START_TIME, SUN_STOP_TIME+1):
        START = True
elif day == os.environ["SPECIAL_DAY"]:
    if today.hour in range(int(os.environ["SPECIAL_PROGRAM_START_TIME"]), int(os.environ["SPECIAL_PROGRAM_STOP_TIME"])):
        START = True


def show_vid():
    if START:
        # url = os.environ["URL"]
        url = os.environ.get("URL", "http://154.118.11.182:8080/shot.jpg")  # this give it a default that can be changed

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
                name = "New member recognized"
                face_dist = face_recognition.face_distance(encode_list_for_known_faces, encodeFace)
                # print(face_dist)
                match_index = np.argmin(face_dist)
                print("match_index gotten", match_index)

                # display bounding box and name on image
                if matches[match_index]:
                    name = classNames[match_index].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                mark_attendance.mark_present(name)
                # else:
                #     mark_attendance(name)

            cv2.imshow("video", img)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
