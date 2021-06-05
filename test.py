import cv2

# openCvVidCapIds = []

# for i in range(100):
#     try:
#         cap = cv2.VideoCapture(i)
#         if cap is not None and cap.isOpened():
#             openCvVidCapIds.append(i)
#         # end if
#     except:
#         pass
#     # end try
# # end for

# print(str(openCvVidCapIds))
frame2 = cv2.imread('/home/vantstein/Desktop/screenon-off-dual-cam/dataset/ss/2.jpg')

lower_cascade = cv2.CascadeClassifier('cascade8.xml')
gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
cv2.imshow('frame',frame2)     
faces2 = lower_cascade.detectMultiScale(
    frame2,
    scaleFactor=1.3,
    minNeighbors=5,
    minSize=(40, 40),
    flags=cv2.CASCADE_SCALE_IMAGE,
    )
for (x,y,w,h) in faces2:
    cv2.rectangle(frame2,(x,y),(x+w,y+h),(255,0,0),2)
    roi_gray = gray2[y:y+h, x:x+w]
    roi_color = frame2[y:y+h, x:x+w]
cv2.imshow('frame2',frame2) 
cv2.waitKey()

