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

@app.route('/registerface')
def registerface():
    print("encoding started")
    time.sleep(0.2)
    if path.exists('encoding.pickle'):
        os.remove('encoding.pickle')
    time.sleep(0.3)
    p = subprocess.Popen(['python', 'encode_faces.py', '-i', 'dataset','-e','encoding.pickle','-d','hog'])
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
    if string == '0':
        p = subprocess.Popen(['python', 'pi_face_recognition.py', '-c', 'haarcascade_frontalface_default.xml','-e','encoding.pickle','-i',name])
        return ('', 204)
    if string == '1':
        p.terminate()
        return ('', 204)

app.run()