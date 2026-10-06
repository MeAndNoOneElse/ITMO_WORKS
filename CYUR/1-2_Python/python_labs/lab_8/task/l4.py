import cv2
import mediapipe as mp
#import time

cap = cv2.VideoCapture(1)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

press_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, c = frame.shape

    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frameRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                             
                cx, cy = int(lm.x*w), int(lm.y*h)
                if id == 8:
                    if (cx > 300) and (cx < 400) and (cy > 100) and (cy < 200):
                        if press_count == 30:
                            cv2.rectangle(frame, (300,100), (400,200), (255, 255, 255), 3)
                            #press_count = 0
                            print ("point")
                        else:
                            cv2.rectangle(frame, (300,100), (400,200), (0, 255, 0), 3)
                            press_count += 1
                            print(f'Press count: {press_count}')
                    else:
                        cv2.rectangle(frame, (300,100), (400,200), (0, 0, 255), 3)
                        press_count = 0        
                    
                '''if (id == 4):
                    if (cx > 300) and (cx < 400) and (cy > 100) and (cy < 200):
                        if press_count == 30:
                            cv2.rectangle(frame, (300,100), (400,200), (255, 255, 255), 3)
                            #press_count = 0
                        print ("big")
                            
                    else:
                        cv2.rectangle(frame, (300,100), (400,200), (0, 0, 255), 3)
                        press_count = 0

                elif(id == 8):
                    if (cx > 300) and (cx < 400) and (cy > 100) and (cy < 200):
                        if press_count == 30:
                            cv2.rectangle(frame, (300,100), (400,200), (255, 255, 255), 3)
                            #press_count = 0
                        print ("point")
                                
                        
                    else:
                        cv2.rectangle(frame, (300,100), (400,200), (0, 0, 255), 3)
                        press_count = 0'''
                        
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
    else:
        cv2.rectangle(frame, (300,100), (400,200), (0, 0, 255), 3)

    cv2.imshow("Image", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
