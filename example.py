import pexpect,os ,sys
from pexpect import *
name = "vanshfpatel@gmail.com"
pin = "3333"
print(name,pin)
filename = str(name) + "^" + str(pin)
message = "Please click on verify pin whenever you resume the session to prevent disruption"
pathx = os.getcwd() + "/dataset/" + str(name) + "/" + filename
pro = "python pi_face_recognition.py -c haarcascade_frontalface_default.xml -e dataset/vanshfpatel@gmail.com/vanshfpatel@gmail.com^5555 -i vanshfpatel@gmail.com"
#p = pexpect.spawn('python pi_face_recognition.py -c haarcascade_frontalface_default.xml -e ' + pathx + ' -i ' + name)
pobj = popen_spawn.PopenSpawn('/bin/bash')
pobj.sendline(str('python app.py'))
