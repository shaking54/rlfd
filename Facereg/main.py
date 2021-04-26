from deepface import DeepFace
import cv2
import os
from multiprocessing import Process

# os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "dummy"
# DeepFace.stream("./database",source="rtsp://192.168.1.6:5554/playlist.m3u")
os.system("mkdir Trung")



# cap = cv2.VideoCapture("rtsp://192.168.1.6:5554/playlist.m3u")
#
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#
#     # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Display the resulting frame
#     cv2.imshow('frame',gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()

