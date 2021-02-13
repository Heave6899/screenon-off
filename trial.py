import numpy as np
import cv2

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
lower_cascade = cv2.CascadeClassifier('cascade8.xml')

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
while 1:
    ret, img = cap.read()
    ret1, img1 = cap2.read()
    gray1 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    lower = face_cascade.detectMultiScale(gray1, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    for (x,y,w,h) in lower:
        img3 = img[y:y+h+100, x:x+w]    
        cv2.imshow('img3',img3)
        cv2.rectangle(img1,(x,y),(x+w,y+h),(0,0,255),2)
        roi_gray = gray1[y:y+h, x:x+w]
        roi_color = img1[y:y+h, x:x+w]   
          
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    cv2.imshow('img',img)
    cv2.imshow('img1',img1)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()