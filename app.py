import base64
from flask import Flask, Response, json, render_template, jsonify, request, url_for, redirect
import os
from os import path
import db, sys
import subprocess
import time
import pexpect.fdpexpect
import sys
import select
if sys.platform.startswith("win"):
    import win32gui
    import win32con
    from os import getpid, system
    from threading import Timer

import multiprocessing

import os
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import subprocess
#test to insert data to the data base

app = Flask(__name__,template_folder="templates")
app.config["DEBUG"] = True

mail = ''
filename = ''
pin = ''
co = 0
count = 0
@app.route('/_photo_cap')
def photo_cap():
    global mail
    global filename
    global frame_h, count
    #photo_base64 = request.args.get('photo_cap')
    #photo_name = str(request.args.get('photo_name'))
    #mail = str(request.args.get('user'))
    photo_name = str(count)
    photo_name = photo_name.zfill(5)
    #header, encoded = photo_base64.split(",", 1)
    #binary_data = base64.b64decode(encoded)
    image_name = str(photo_name)+".jpeg"

    if path.exists(os.path.join("dataset",mail)):
        # with open(os.path.join("dataset",mail,image_name), "wb") as f:
        #     f.write(binary_data)
        cv2.imwrite(os.path.join("dataset",mail,image_name), frame_h)
        count = count +1 
        print(count)
    else:
        os.mkdir(os.path.join("dataset",mail))
        time.sleep(0.3)
        # with open(os.path.join(mail,image_name), "wb") as f:
        #     f.write(binary_data)
        cv2.imwrite(os.path.join("dataset",mail,image_name), frame_h)
        count = count +1 
        print(count)
    response = 'success'
    

        #os.system("python encode_faces.py -i dataset -e encoding.pickle  -d hog")
        #os.system("python ")
    return jsonify(response=response)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html', email = mail)

@app.route('/stop')
def stop():
    return render_template('stop.html', email = mail)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register')
def register():
    return render_template('register.html', email = mail)

frame_h = 0
pause = 0
def gen_frames():
    camera1 = cv2.VideoCapture(0)
    camera1.set(cv2.CAP_PROP_BUFFERSIZE, 2) 
    camera2 = cv2.VideoCapture(1)
    camera2.set(cv2.CAP_PROP_BUFFERSIZE, 2) 
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    global pause
    global frame_h
    print(pause)
    while 1:
        if pause == 0 and count < 15:
            success1, frame1 = camera1.read() 
            success2, frame2 = camera2.read() # read the camera frame
            if not success1 or not success2:
                break
            else:
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray1,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(40, 40),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                lowers = face_cascade.detectMultiScale(
                    gray2,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(40, 40),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                    )
                #print(body)
                for (x,y,w,h) in faces:
                    cv2.rectangle(frame1,(x,y),(x+w,y+h),(255,0,0),2)
                    roi_gray = gray1[y:y+h, x:x+w]
                    roi_color = frame1[y:y+h, x:x+w]
                for (x,y,w,h) in lowers:
                    cv2.rectangle(frame2,(x,y),(x+w,y+h),(0,0,255),2)
                    roi_gray = gray2[y:y+h, x:x+w]
                    roi_color = frame2[y:y+h+50, x:x+w]
                    

                # for (x,y,w,h) in body:
                #     cv2.rectangle(frame1,(x,y),(x+w,y+h),(255,255,0),2)
                #     roi_gray = gray1[y:y+h, x:x+w]
                #     roi_color = frame1[y:y+h, x:x+w]
                
                frame_h = cv2.hconcat([frame1,frame2])
                ret, buffer = cv2.imencode('.jpg', frame_h)
                frame = buffer.tobytes()
                
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        else:
            if count > 15:
                cv2.destroyAllWindows()
                camera1.release()
                camera2.release()

@app.route('/pauseplay')
def pause_fn():
    global pause
    if pause == 1:
        pause = 0
    else:
        pause = 1
    return jsonify(response = 'ok')
@app.route('/checkmail')
def checkmail():
    global mail
    global co
    mail = request.args.get('mail')
    #filename = str(mail) + "^" + str(pin)
    #pathx = os.getcwd() + "/dataset/" + str(mail) + "/" + filename 
    pathx = os.getcwd() + "/dataset/" + mail
    if path.exists(os.getcwd() + "/dataset/" + mail):
        if co < 3:
            x = detectface(pathx,mail)
            print(co)
            if x == 1:
                return jsonify(url = url_for('start'))
            else:
                co += 1
                return jsonify(response = "Error, user face not recognised")
        else:
            co = 0
            return jsonify(response = "User incorrect, try again")
    else:
        return jsonify(url = url_for('register'))

@app.route('/_registerface')
def registerface():
    global filename
    name = request.args.get('name')
    pin = request.args.get('pin')
    print("encoding started")
    time.sleep(0.3)
    filename = str(name) + "^" + str(pin)
    path = os.getcwd() + "/dataset/" + str(name) + "/"
    p = subprocess.Popen(['python', 'encode_faces.py', '-i', path,'-e',path + filename,'-d','cnn'])
    (output, err) = p.communicate()  
    p_status = p.wait()
    p.terminate()
    startsession("0")
    url = url_for('stop')
    return jsonify(url = url)

p = 0
@app.route('/_start_session')
def startsession(*type):
    global p
    global filename
    string = request.args.get('type')
    name = request.args.get('name')
    pin = request.args.get('pin')
    print(string,name,pin, type)
    filename = str(name) + "^" + str(pin)
    message = "Please click on verify pin whenever you resume the session to prevent disruption"
    pathx = os.getcwd() + "/dataset/" + str(name) + "/" + filename 
    if string == '0' or '0' in type:
        p = subprocess.Popen(['python', 'pi_face_recognition.py', '-c', 'haarcascade_frontalface_default.xml','-e',pathx,'-i',name],stdin=subprocess.PIPE)
        url = url_for('stop')
        return jsonify(url = url, message = message, email = mail)
    if string == '1':
        if path.exists(pathx):
            p.terminate()
            url = url_for('index')
            return jsonify(url = url, correct='1')
        else:
            return jsonify(message = "Error wrong pin", correct = '0')
count = 0

def detectface(p, mail):
    prefixed = [filename for filename in os.listdir(p) if filename.startswith(mail)]
    data = pickle.loads(open(p+"/"+prefixed[0], "rb").read())
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    camera1 = cv2.VideoCapture(0)
    camera1.set(cv2.CAP_PROP_FRAME_WIDTH , 352)
    camera1.set(cv2.CAP_PROP_FRAME_HEIGHT , 288)
    camera2 = cv2.VideoCapture(1)
    camera2.set(cv2.CAP_PROP_FRAME_WIDTH , 352)
    camera2.set(cv2.CAP_PROP_FRAME_HEIGHT , 288) 
    success2, frame2 = camera2.read()
    success1, frame1 = camera1.read()
    time.sleep(0.2)
    camera1.release()
    camera2.release()
    cv2.destroyAllWindows()
    #frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    frame = cv2.hconcat([frame1,frame2])
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
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
            print(name)
        # update the list of names
        names.append(name)
    if mail in names:
        print(names.count(mail)) 
        if(names.count(mail) >= 2):
            return 1
        else:
            return 0
    else:
        return 0

@app.route('/_checkpin')
def checkpin():
    print(type(p))
    global count
    global pin
    global mail
    pin = request.args.get('pin')
    pin = str.encode(pin)
    f = open("pin", "wb")
    f.write(pin)
    f.close()
    # pin = pin
    #pin = str.encode(pin)
    # for line in iter(p.stdout.readline):
    #     line = line.decode()
    #     print(line)
    #     sys.stdout.flush()
    # p.stdin.write(pin)
    # print("stdin done!")
    # x = p.stdout.readline()
    # x = x.decode()
    # print(x)
    
    #p.stdin.write(pin)
    time.sleep(30)
    f = open("pin", "rb")
    corbool = f.readline()
    f.close()
    corbool = corbool.decode()
    print(corbool)
    if corbool == "1":
        m = "Correct pin, resumed session"
        pin = ''
        return jsonify(message = m)
    else:
        m = "Error, you have " + str(2-count) + " chances remaining"
        count += 1
        if count == 3:
            m = "You are locked out! Shutting down computer"
            return jsonify(message = m)
        return jsonify(message = m)
    
@app.route('/_startingpin')
def startpin():
    pin = request.args.get('pin')
    name = request.args.get('mail')
    print(type(name))
    filename = str(name) + "^" + str(pin)
    pathx = os.getcwd() + "/dataset/" + str(name) + "/" + filename 
    if path.exists(pathx):
        print("yes")
        m = "Please click on start button to start the process"
        return jsonify(response = m, correct = "1")
    else:
        error = "Invalid Pin, Please try again"
        return jsonify(response = error, correct = "0")

app.run()