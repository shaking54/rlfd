import os
import face_recognition
import cv2
from gevent import monkey
from datetime import datetime
import numpy as np
import threading
from multiprocessing import Process
import time
import json
from gevent.server import StreamServer
from mprpc.server import RPCServer


def SerializeJson(list_logs):
    t = datetime.now().strftime('%d-%m-%Y---%H-%M-%S')
    jsonfile = open("E:\\PycharmProjects\\IPCtest\\logs\\" + str(t) + '.json', 'w')
    for i in list_logs:
        jsonfile.write(i)
        jsonfile.write("\n")
    jsonfile.close()
    list_logs.clear()


def stream(ip, buffer):
    # print(threading.currentThread().getName(), 'Starting')
    capture = cv2.VideoCapture(0)
    # capture.set(cv2.CAP_PROP_BUFFERSIZE,2)
    while capture.isOpened():
        ret, frame = capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        buffer.append((ret, small_frame))
        face_locations = face_recognition.face_locations(small_frame)
        try:
            (top, right, bottom, left) = face_locations[0]
            cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom * 4), (0, 0, 255), 2)
        except:
            print("No face")
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1 / 60)
    cv2.destroyAllWindows()
    # print(threading.currentThread().getName(), 'Exit')


def processing(db_path, ip, buffer):
    # print(threading.currentThread().getName(), 'Starting')
    path_folder = os.listdir(str(db_path))
    image = []
    path = str(db_path)
    for i in path_folder:
        image.append(os.listdir(path + i))
    know_face_encodings = []
    know_face_names = []
    for i, j in zip(path_folder, image):
        strings = str(j).strip("'[]'")
        images = face_recognition.load_image_file(path + "/" + str(i) + "/" + strings)
        face_encoding = face_recognition.face_encodings(images)[0]
        know_face_names.append(i)
        know_face_encodings.append(face_encoding)
    list_logs = []
    print(len(buffer))
    while True:
        print("processing")
        for i, (ret, frame) in enumerate(buffer):
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(frame)
            print("face locations", face_locations)
            if face_locations is None:
                print("None")
                continue
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(know_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(know_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = know_face_names[best_match_index]

                face_names.append(name)


            for (top, right, bottom, left), name in zip(face_locations, face_names):
                dict = {
                    "time": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    "region": (top * 4, right * 4, bottom * 4, left * 4),
                    "name": name,
                    "camera-ip": ip
                }
                data_json = json.dumps(dict)
                list_logs.append(data_json)

            print("list_log", len(list_logs))
            if len(list_logs) >= 10:
                print("write logs")
                SerializeJson(list_logs)
        time.sleep(1)
    # print(threading.currentThread().getName(), 'Exit')


# class Core:
#
#     @staticmethod
#     def stream(ip, buffer):
#         # print(threading.currentThread().getName(), 'Starting')
#         capture = cv2.VideoCapture(0)
#         # capture.set(cv2.CAP_PROP_BUFFERSIZE,2)
#         while capture.isOpened():
#             ret, frame = capture.read()
#             small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#             buffer.append((ret, small_frame))
#             face_locations = face_recognition.face_locations(small_frame)
#             try:
#                 (top, right, bottom, left) = face_locations[0]
#                 cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom * 4), (0, 0, 255), 2)
#             except:
#                 print("No face")
#             cv2.imshow('Video', frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#             time.sleep(1/60)
#         cv2.destroyAllWindows()
#         # print(threading.currentThread().getName(), 'Exit')
#
#     @staticmethod
#     def processing(db_path, ip, buffer):
#         # print(threading.currentThread().getName(), 'Starting')
#         path_folder = os.listdir(str(db_path))
#         image = []
#         path = str(db_path)
#         for i in path_folder:
#             image.append(os.listdir(path + i))
#         know_face_encodings = []
#         know_face_names = []
#         for i, j in zip(path_folder, image):
#             strings = str(j).strip("'[]'")
#             images = face_recognition.load_image_file(path + "/" + str(i) + "/" + strings)
#             face_encoding = face_recognition.face_encodings(images)[0]
#             know_face_names.append(i)
#             know_face_encodings.append(face_encoding)
#         list_logs = []
#         print(len(buffer))
#         while True:
#             print("processing")
#             for i, (ret, frame) in enumerate(buffer):
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#                 face_locations = face_recognition.face_locations(small_frame)
#                 if face_locations is None:
#                     print("None")
#                     continue
#                 face_encodings = face_recognition.face_encodings(small_frame, face_locations)
#                 face_names = []
#                 for face_encoding in face_encodings:
#                     matches = face_recognition.compare_faces(know_face_encodings, face_encoding)
#                     name = "Unknown"
#
#                     face_distances = face_recognition.face_distance(know_face_encodings, face_encoding)
#                     best_match_index = np.argmin(face_distances)
#                     if matches[best_match_index]:
#                         name = know_face_names[best_match_index]
#
#                     face_names.append(name)
#
#                 for (top, right, bottom, left), name in zip(face_locations, face_names):
#                     dict = {
#                         "time": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
#                         "region": (top * 4, right * 4, bottom * 4, left * 4),
#                         "name": name,
#                         "camera-ip": ip
#                     }
#                     data_json = json.dumps(dict)
#                     list_logs.append(data_json)
#
#                 print(len(list_logs))
#                 if len(list_logs) >= 10:
#                     print("write logs")
#                     SerializeJson(list_logs)
#             time.sleep(1)
#         # print(threading.currentThread().getName(), 'Exit')
#
#     @staticmethod
#     # tao image folder cho nhan vien moi
#     def register_db_path(db_path, name):
#         path = db_path + name
#         if os.path.exists(path):
#             os.makedirs(path)
#
#     @staticmethod
#     # luu hinh anh nhan vien
#     def registeremployee(db_path_name):
#         return 0

monkey.patch_all()


class DeepFaceServer(RPCServer):

    @staticmethod
    def stream_(buffer):
        print("stream")
        with open("E:/PycharmProjects/Facereg/settings.json") as f:
            settings = json.loads(f.read())
        Core.stream(settings['source'], buffer)

    @staticmethod
    def process(buffer):
        print("process")
        with open("E:/PycharmProjects/Facereg/settings.json") as f:
            settings = json.loads(f.read())
        Core.processing(settings['db_path'], settings['source'], buffer)

    @staticmethod
    def stream_process():
        print("stream and process")
        with open("E:/PycharmProjects/Facereg/settings.json") as f:
            settings = json.loads(f.read())
        buffer = []
        thread1 = threading.Thread(target=stream, args=(settings['source'], buffer))
        thread2 = threading.Thread(target=processing, args=(settings['db_path'], settings['source'], buffer))
        thread1.start()
        thread2.start()
        #thread1.join()
        #thread2.join()


print("--running--")
server = StreamServer(('127.0.0.1', 6000), DeepFaceServer())
server.serve_forever()
