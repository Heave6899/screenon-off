# USAGE
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
import sys
import select
if sys.platform.startswith("win"):
    import win32gui
    import win32con
    from os import getpid, system
    from threading import Timer

import multiprocessing

try:
    from picamera.array import PiRGBArray

    print("module 'picamera' is installed")
except ModuleNotFoundError:
    print("module 'picamera' is not installed")

try:
    from picamera import PiCamera

    print("module 'picamera' is installed")
except ModuleNotFoundError:
    print("module 'picamera' is not installed")
import os
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import subprocess

# import paho.mqtt.client as mqtt

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("iotscreenoff/#")

# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))

# #def publish(client, userdata, flags,rc):
# #    client.publish("iotscreenoff/monitor","OFF")
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect("broker.hivemq.com", 1883, 60)
# client.loop_start()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    "-c", "--cascade", required=True, help="path to where the face cascade resides"
)
ap.add_argument(
    "-e", "--encodings", required=True, help="path to serialized db of facial encodings"
)
ap.add_argument("-i", "--idhash", required=True, help="id of person")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
def force_exit():
    pid = getpid()
    system("taskkill /pid %s /f" % pid)

pincode = args["encodings"]
pincode = pincode.split("^")
pincode = pincode[1]
print(type(pincode))

flagpin = 1

def pin():
    global flagpin
    global t1
    global flag
    while True:
        if flagpin == 0:
            print("Please enter pin")
            m, n, o = select.select( [sys.stdin], [], [], 10 )
            if (m):
                x = sys.stdin.readline().strip()
                if x == pincode:
                    stopping()
                    flagpin = 1
                    return
                else:
                    if not t1.is_alive():
                        flag = 1
                        t1 = multiprocessing.Process(
                                target=run,
                            )
                        t1.start()
                        return 
                    return
            else:
                if not t1.is_alive():
                    flag = 1
                    t1 = multiprocessing.Process(
                            target=run,
                        )
                    t1.start()
                    return 
                return

def stopping():
    print(type(t1))
    t1.terminate()
    print("TERMINATED:", t1, t1.is_alive())
    t1.join()
    print("JOINED:", t1, t1.is_alive())
    if sys.platform.startswith("linux"):
        subprocess.call(["xset", "-display", ":0", "dpms", "force", "on"])
def run():
    while True:
        if sys.platform.startswith("linux"):
            s = str(subprocess.check_output("xset -q", shell=True))
            if "Monitor is On" in s:
                subprocess.call("xset -display :0.0 dpms force off", shell=True)
        elif sys.platform.startswith("win"):
            s = str(
                os.system(
                    'cmd /k "wmic path win32_desktopmonitor GET Availability,Caption"'
                )
            )
            if "8" in s:
                t = Timer(1, force_exit)
                t.start()
                SC_MONITORPOWER = 0xF170
                win32gui.SendMessage(
                    win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, SC_MONITORPOWER, 2
                )
                t.cancel()
        elif sys.platform.startswith("darwin"):
            subprocess.call(
                "echo 'tell application \"Finder\" to sleep' | osascript", shell=True
            )

        print("Thread running")
        time.sleep(0.5)


if "picamera" in sys.modules:
    camera = PiCamera()
    camera.resolution = (300, 300)
    # camera.framerate = 3
    rawCapture = PiRGBArray(camera, size=(300, 300))
    time.sleep(2.0)

    # start the FPS counter
    # fps = FPS().start()
    camera.framerate = 3

    # loop over frames from the video file stream
    # while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)

    # frame = vs.read()
    # frame = imutils.resize(frame, width=500)
    i = 0
    flag = 0
    for image in camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True
    ):
        frame = image.array

        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        if len(rects) == 0:
            j = j + 1
            print(j)
            if j == 7:
                flag = 1
                # client.publish("iotscreenoff/monitor","OFF, Flag = 0")
                t1 = multiprocessing.Process(
                    target=run,
                )
                t1.start()
        else:
            j = 0
            print("Restart", str(j))
            if flag == 1:
                # subprocess.call(["xset", "-display",":0","dpms","force","on"])
                flag = 0
                print(type(t1))
                t1.terminate()
                print("TERMINATED:", t1, t1.is_alive())
                t1.join()
                print("JOINED:", t1, t1.is_alive())
                subprocess.call(["xset", "-display", ":0", "dpms", "force", "on"])

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(
                frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2
            )

        # display the image to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # update the FPS counter
        # fps.update()
        rawCapture.truncate(0)

    # stop the timer and display FPS information
    # fps.stop()
    # print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
if "picamera" not in sys.modules:
    j = 0
    flag = 0
    t1 = 0
    while True:
        camera = cv2.VideoCapture(0)
        framerate = camera.get(5)
        # camera.resolution = (300,300)
        # camera.framerate = 3
        ret, frame = camera.read()
        camera.release()
        time.sleep(0.7)

        # frame = frame.array

        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
        print(names)

        if len(rects) == 0 or args["idhash"] not in names:
            j = j + 1
            print(j)
            if j == 10:
                flag = 1
                # client.publish("iotscreenoff/monitor","OFF, Flag = 0")
                t1 = multiprocessing.Process(
                    target=run,
                )
                t1.start()
        else:
            j = 0
            print("Restart", str(j))
            if flag == 1:
                # subprocess.call(["xset", "-display",":0","dpms","force","on"])
                flag = 0
                stopping()
                flagpin = 0
                # t2 = multiprocessing.Process(target=pin,)
                # t2.start()
                pin()
                
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(
                frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2
            )

        # display the image to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        # if key == ord("q"):
        # 	break

        # update the FPS counter
        # fps.update()
        time.sleep(1)

    cv2.destroyAllWindows()
# vs.stop()
