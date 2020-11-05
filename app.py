import base64
from flask import Flask, Response, json, render_template, jsonify, request
import os
from os import path
import db
import subprocess
import time

#test to insert data to the data base

app = Flask(__name__)


@app.route("/test")
def test():
    db.db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"


@app.route('/photo')
def photo():
    return render_template('index.html')


@app.route('/_photo_cap')
def photo_cap():
    photo_base64 = request.args.get('photo_cap')
    photo_name = str(request.args.get('photo_name'))
    user = str(request.args.get('user'))
    photo_name = photo_name.zfill(5)
    header, encoded = photo_base64.split(",", 1)
    binary_data = base64.b64decode(encoded)
    image_name = str(photo_name)+".jpeg"

    if path.exists(os.path.join("dataset",user)):
        with open(os.path.join("dataset",user,image_name), "wb") as f:
            f.write(binary_data)
    else:
        os.mkdir(os.path.join("dataset",user))
        time.sleep(0.3)
        with open(os.path.join(user,image_name), "wb") as f:
            f.write(binary_data)

    response = 'ok'
    

        #os.system("python encode_faces.py -i dataset -e encoding.pickle  -d hog")
        #os.system("python ")
    return jsonify(response=response)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkmail',methods=['POST'])
def checkmail():
    mail = request.form['mail']
    print(mail)
    if path.exists(os.getcwd() + "/dataset/" + mail):
        return render_template('start.html',email = mail)
    else:
        return render_template('register.html')

@app.route('/_registerface')
def registerface():
    name = request.args.get('name')
    pin = request.args.get('pin')
    print("encoding started")
    time.sleep(0.2)
    time.sleep(0.3)
    filename = str(name) + "^" + str(pin)
    path = os.getcwd() + "/dataset/" + str(name) + "/"
    p = subprocess.Popen(['python', 'encode_faces.py', '-i', path,'-e',filename,'-d','hog'])
    (output, err) = p.communicate()  
    p_status = p.wait()
    p.terminate()
    return ('', 204)

p = 0
@app.route('/_start_session')
def startsession():
    global p
    string = request.args.get('type')
    name = request.args.get('name')
    pin = request.args.get('pin')
    print(string,name,pin)
    filename = str(name) + "^" + str(pin)
    path = os.getcwd() + "/dataset/" + str(name) + "/" + filename 
    if string == '0':
        p = subprocess.Popen(['python', 'pi_face_recognition.py', '-c', 'haarcascade_frontalface_default.xml','-e',path,'-i',name],stdin=subprocess.PIPE)
        return ""
    if string == '1':
        p.terminate()
        return ""

@app.route('/checkpin')
def checkpin():
    print(type(p))
    pin = request.args.get('pin')
    pin = str.encode(pin)
    p.communicate(input=pin)
    return ""
app.run()