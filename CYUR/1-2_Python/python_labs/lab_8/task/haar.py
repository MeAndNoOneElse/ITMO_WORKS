import cv2


plateCascade = cv2.CascadeClassifier('haarcascade_plate_number.xml')
minArea = 500

img = cv2.imread('im14.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

plates = plateCascade.detectMultiScale(gray, 1.1, 4)

for (x, y, w, h) in plates:
    area = w * h
    if area > minArea:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        imgROI = img[y:y+h, x:x+w]
        cv2.imshow('ROI', imgROI)
cv2.imshow("image", img)

cv2.waitKey(0)
cv2.destroyAllWindows()