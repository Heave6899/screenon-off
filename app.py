import base64
from flask import Flask, Response, json, render_template, jsonify, request, url_for, redirect
import os
from os import path
import db, sys
import subprocess
import time
import pexpect.fdpexpect
#test to insert data to the data base

app = Flask(__name__,template_folder="templates")
app.config["DEBUG"] = True

mail = ''
filename = ''
pin = ''

@app.route('/_photo_cap')
def photo_cap():
    global mail
    global filename
    photo_base64 = request.args.get('photo_cap')
    photo_name = str(request.args.get('photo_name'))
    mail = str(request.args.get('user'))
    photo_name = photo_name.zfill(5)
    header, encoded = photo_base64.split(",", 1)
    binary_data = base64.b64decode(encoded)
    image_name = str(photo_name)+".jpeg"

    if path.exists(os.path.join("dataset",mail)):
        with open(os.path.join("dataset",mail,image_name), "wb") as f:
            f.write(binary_data)
    else:
        os.mkdir(os.path.join("dataset",mail))
        time.sleep(0.3)
        with open(os.path.join(mail,image_name), "wb") as f:
            f.write(binary_data)

    response = 'ok'
    

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

@app.route('/register')
def register():
    return render_template('register.html', email = mail)

@app.route('/checkmail')
def checkmail():
    global mail
    mail = request.args.get('mail')
    pin = request.args.get('pin')
    filename = str(mail) + "^" + str(pin)
    pathx = os.getcwd() + "/dataset/" + str(mail) + "/" + filename 
    if path.exists(os.getcwd() + "/dataset/" + mail):
        if path.exists(pathx):
            return jsonify(url = url_for('start'))
        else:
            return jsonify(response = "Error, incorrect pin")
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
    p = subprocess.Popen(['python', 'encode_faces.py', '-i', path,'-e',path + filename,'-d','hog'])
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
    time.sleep(10)
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
        m = "Error, you have " + str(3-count) + " chances remaining"
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