import base64
from flask import Flask, Response, json, render_template, jsonify, request, url_for, redirect
import os
from os import path
import sys
import subprocess
import time
from deepface import DeepFace
import pexpect.fdpexpect
import sys
import select
if sys.platform.startswith("win"):
    import win32gui
    import win32con
    from os import getpid, system
    from threading import Timer

import multiprocessing
from ctypes import c_wchar_p

import os
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import subprocess
from deepface import DeepFace
from cryptography.fernet import Fernet

#face cascades
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
lower_cascade = cv2.CascadeClassifier('cascade8.xml')

#backend
backend = "ssd"

#encrypted key
key = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F9AY='
cipher_suite = Fernet(key)

app = Flask(__name__,template_folder="templates")
app.config["DEBUG"] = True

global_mail = ''
j = 0
flag = 0
t1 = 0
flagpin = 0
global_filename = ''
global_pin = ''
check_pin = ''
co = 0
count = 0
p = 0
pause = 0
detectedface = 0
# manager
manager = multiprocessing.Manager()
check_pin = manager.Value(c_wchar_p,'')

@app.route('/_photo_cap')
def photo_cap():
    global global_mail
    global filename
    global frame_h, count
    photo_name = str(count)
    photo_name = photo_name.zfill(5)
    image_name1 = "1.jpg"
    image_name2 = "2.jpg"
    if path.exists(os.path.join("dataset",global_mail)):
        cv2.imwrite(os.path.join("dataset",global_mail,image_name1), frame_h[0])
        cv2.imwrite(os.path.join("dataset",global_mail,image_name2), frame_h[1])
        count = count + 1 
        print(count)
    else:
        os.mkdir(os.path.join("dataset",global_mail))
        time.sleep(0.3)
        cv2.imwrite(os.path.join("dataset",global_mail,image_name1), frame_h[0])
        cv2.imwrite(os.path.join("dataset",global_mail,image_name2), frame_h[1])
        count = count + 1 
        print(count)
    response = 'success'
    return jsonify(response=response)

@app.route('/',methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html', email = global_mail)

@app.route('/stop')
def stop():
    return render_template('stop.html', email = global_mail)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register')
def register():
    return render_template('register.html', email = global_mail)


def gen_frames():
    camera1 = cv2.VideoCapture(0)
    camera1.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    width1  = camera1.get(cv2.CAP_PROP_FRAME_WIDTH) 
    height1 = camera1.get(cv2.CAP_PROP_FRAME_HEIGHT)
    camera2 = cv2.VideoCapture(1)
    camera2.set(cv2.CAP_PROP_BUFFERSIZE, 2) 
    width2  = camera2.get(cv2.CAP_PROP_FRAME_WIDTH) 
    height2 = camera2.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(height1,width1,height2,width2)
    global pause
    global frame_h
    global detectedface
    global face_cascade
    print(pause)
    while 1:
        if pause == 0 and count < 1:
            success1, frame1 = camera1.read()
            success2, frame2 = camera2.read() 
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            faces1 = face_cascade.detectMultiScale(
                gray1,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(40, 40),
                flags=cv2.CASCADE_SCALE_IMAGE,
                )
            for (x,y,w,h) in faces1:
                cv2.rectangle(frame1,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray1[y:y+h, x:x+w]
                roi_color = frame1[y:y+h, x:x+w]
            faces2 = lower_cascade.detectMultiScale(
                gray2,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(40, 40),
                flags=cv2.CASCADE_SCALE_IMAGE,
                )
            for (x,y,w,h) in faces2:
                cv2.rectangle(frame2,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray1[y:y+h, x:x+w]
                roi_color = frame1[y:y+h, x:x+w]

            cv2.rectangle(frame1,(int(width1*0.25),int(height1*0.25)),(int(width1*0.75),int(height1*0.75)),(0,0,0),3)
            cv2.rectangle(frame2,(int(width2*0.25),int(height2*0.25)),(int(width2*0.75),int(height2*0.75)),(0,0,0),3)

            frame = cv2.hconcat([frame1, frame2])
            frame_h = [frame1,frame2]
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        else:
            if count >= 1 or detectedface == 1:
                print("destroyed")
                cv2.destroyAllWindows()
                camera1.release()
                camera2.release()

@app.route('/pauseplay', methods =['GET'])
def pause_fn():
    global pause
    if pause == 1:
        pause = 0
    else:
        pause = 1
    return jsonify(response = 'ok')
    
@app.route('/_checkmail',methods=['GET'])
def checkmail():
    global global_mail
    global co
    print("insidecheckmail")
    global_mail = request.args.get('mail')
    pathx = os.getcwd() + "/dataset/" + global_mail
    if path.exists(os.getcwd() + "/dataset/" + global_mail):
        if co < 3:
            x = detectface(pathx,global_mail)
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

@app.route('/_registerface', methods=['GET'])
def registerface():
    global global_filename
    global global_pin
    # global_mail = request.args.get('mail')
    global_pin = request.args.get('pin')
    print("encoding started")
    time.sleep(0.3)
    global_filename = "pin.vnt"
    path = os.getcwd() + "/dataset/" + str(global_mail) + "/"
    file = open(path+global_filename,'wb')
    file.write(cipher_suite.encrypt(bytes(global_pin,'utf-8')))
    file.close()
    #p = subprocess.Popen(['python', 'encode_faces.py', '-i', path,'-e',path + filename,'-d','cnn'])
    startsession("0")
    url = url_for('stop')
    return jsonify(url = url)


@app.route('/_start_session',methods=['GET'])
def startsession(*type):
    global p,global_mail, global_pin
    string = request.args.get('type')
    name = request.args.get('name')
    pin = request.args.get('pin')
    print(string,name,pin, global_pin)
    message = "Please click on verify pin whenever you resume the session to prevent disruption"
    if string == '0' or '0' in type:
        p = multiprocessing.Process(
                    target=pi_face_recognition, args=(check_pin,)
                )        
        p.start()
        url = url_for('stop')
        return jsonify(url = url, message = message, email = global_mail)
        # return redirect(url_for('stop'))
    if string == '1':
        if global_pin == pin:
            p.terminate()
            p.join()
            # stopping()
            url = url_for('index')
            return jsonify(url = url, correct='1')
        else:
            return jsonify(message = "Error wrong pin", correct = '0')

def detectface(p, global_mail):
    global frame_h
    global detectedface
    print("insidedetectface")
    
    pathimg1 = path.join(os.getcwd() + "/dataset/" + global_mail + "/1.jpg")
    pathimg2 = path.join(os.getcwd() + "/dataset/" + global_mail + "/2.jpg")
    count = 0
    #img1 = cv2.imread(pathimg1,1)
    #img2 = cv2.imread(pathimg2,2)
    while 1:
        count += 1
        try:
            if count%10 == 0:
                frame1 = frame_h[0]
                frame2 = frame_h[1]
                resultimg  = DeepFace.verify([[frame1, pathimg1],[frame2,pathimg2]],  model_name = 'Dlib', detector_backend = backend, enforce_detection = False)
                print(resultimg)
        except Exception:
            print("returndetectface")
            return 0
        if count%10 == 0:
            if resultimg["pair_1"]["verified"] and resultimg["pair_2"]["verified"]:
                detectedface = 1
                print("returndetectface")
                return 1  
            else:
                if count%10==0:
                    if count == 300:
                        print("returndetectface")
                        return 0 


@app.route('/_checkpin',methods=['GET'])
def checkpin():
    global count
    global global_pin
    global global_mail
    global check_pin, t1
    pin = request.args.get('pin')
    check_pin.value = pin
    print("nice",check_pin.value)
    if global_pin == pin:
        print("checked pin:",check_pin)
        m = "Correct pin, resumed session"
        return jsonify(message = m)
    else:
        m = "Error, you have " + str(2-count) + " chances remaining"
        count += 1
        if count == 3:
            m = "You are locked out! Shutting down computer"
            return jsonify(message = m)
        return jsonify(message = m)
    
@app.route('/_startingpin',methods=['GET'])
def startpin():
    global global_pin, global_mail
    print(global_pin, global_mail)
    getpin = request.args.get('pin')
    filename = "pin.vnt"
    file = open(os.getcwd()+"/dataset/"+global_mail+"/"+filename,'rb')
    pin = file.readline()
    file.close()
    print(pin)
    pin = cipher_suite.decrypt(bytes(pin)).decode('utf-8')
    print(pin)
    if pin == getpin:
        global_pin = pin
        m = "Please click on start button to start the process"
        return jsonify(response = m, correct = "1")
    else:
        error = "Invalid Pin, Please try again"
        return jsonify(response = error, correct = "0")

def pi_face_recognition(input_pin):
    global global_mail
    global t1
    global j
    global backend
    global flag
    while True:
        # time.sleep(5)
        camera1 = cv2.VideoCapture(0)
        camera2 = cv2.VideoCapture(1)
        
        success1, frame1 = camera1.read() 
        success2, frame2 = camera2.read() 
        while not success1 or success2:
            success1, frame1 = camera1.read()
            success2, frame2 = camera2.read()
        framerate1 = camera1.get(5)
        framerate2 = camera2.get(5)
        camera1.release()
        camera2.release()
        pathimg1 = path.join(os.getcwd() + "/dataset/" + global_mail + "/1.jpg")
        pathimg2 = path.join(os.getcwd() + "/dataset/" + global_mail + "/2.jpg")
        img1 = cv2.imread(pathimg1,1)
        img2 = cv2.imread(pathimg2,2)
        # try:
        resultimg  = DeepFace.verify([[frame1, pathimg1],[frame2,pathimg2]],  model_name = 'Dlib', detector_backend = backend, enforce_detection = False)
        print(resultimg)
        time.sleep(5)
        # except Exception:
        #     resultimg = {'pair_1': {'verified':False}, 'pair_2':{'verified':False}}
        if not (resultimg['pair_1']['verified'] and resultimg['pair_2']['verified']):
            j = j + 1
            print("j",j)
            if j == 10:
                flag = 1
                # client.publish("iotscreenoff/monitor","OFF, Flag = 0")
                t1 = multiprocessing.Process(
                    target=runit,
                )
                t1.start()
        else:
            j = 0
            if flag == 1:
                # subprocess.call(["xset", "-display",":0","dpms","force","on"])
                flag = 0
                stopping()
                flagpin = 0
                print("Please enter pin")
                time.sleep(15)
                pi_pin(input_pin)

def pi_pin(input_pin):
    global flagpin
    global t1
    global check_pin
    global flag
    global count, global_mail
    filename = "pin.vnt"
    file = open(os.getcwd()+"/dataset/"+global_mail+"/"+filename,'rb')
    pin = file.readline()
    pin = cipher_suite.decrypt(bytes(pin)).decode('utf-8')
    file.close()
    print("pipin:",input_pin.value,"pin:",pin)
    if count == 3:
        exit()
    while True:
        if flagpin == 0:
            if pin == input_pin.value:
                if t1.is_alive():
                    stopping()
                flagpin = 1
                count = 0
                return
            else:
                if not t1.is_alive():
                    flag = 1
                    t1 = multiprocessing.Process(
                            target=runit,
                        )
                    t1.start()
                    count += 1
                    return 
            
def stopping():
    t1.terminate()
    t1.join()
    if sys.platform.startswith("linux"):
        subprocess.call(["xset", "-display", ":0", "dpms", "force", "on"])

def runit():
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
        print("tr")
        time.sleep(0.5)

app.run()