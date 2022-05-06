import cv2
import mediapipe as mp
import time
import serial
# from PIL import ImageFont, ImageDraw, Image #For Hebrew font

# segment[0] is to be the cartesian (0,0,0) - the absolute value of (segment(n>0)-segment[0]) makes segment[0] act as axix origin

interface = {"open": True, "segment": 0,
             "palm_direction": 1}  # 0 is palm 1 is back

FINGER_BIN = ["1", "1", "1", "1"]
SEGMENT_POS = {}
CONTROLLER = {0: "SLEEP", 1: "LISTEN", 2: "FUCK YOU", 3: "TWAT", 4: "", 5: "re",
              6: "", 7: "WAKE UP", 8: "EXIT", 9: "", 10: "", 11: "", 12: "", 13: "FUCK OFF", 14: "COME HERE", 15: "STOP"}

#Open serial port
# ser = serial.Serial('COM4', 9600)
# ser.timeout =1

# This fucntion make segment[0].y the origin of the hands y axis


def originize_seg_zero(segments):
    for i in range(1, len(segments)):
        # Putting this on abs will make up pointing fingers have same value as down pointing, If axis originizer is not abs, binary values inverse by y scale direction.
        segments[i].y = segments[i].y-segments[0].y
        # segments[i].x = segments[i].x-segments[0].x
    # segments[0].y = 0
    return segments


def segment_abs_difference(tip, knuckle):  # Currently supperts y axis only
    #  '<' makes upward pointing positive, and vice verca
    if interface["palm_direction"] == 1:
        return str(int(SEGMENT_POS[tip].y-SEGMENT_POS[knuckle].y <= 0))
    else:
        return str(int(SEGMENT_POS[tip].y-SEGMENT_POS[knuckle].y > 0))

# Determines palm orientaion, palm of hand facing, or back hand facing


def palm_or_back():
    return int(SEGMENT_POS[17].x-SEGMENT_POS[11].x > 0)


def keyboard_GUI(interface):
    key = cv2.waitKey(1)
    if key == ord('x'):
        interface["open"] = False
    return interface

# finger to binary gimic
def finger_binary_monitor():
    global FINGER_BIN
    FINGER_BIN[0] = segment_abs_difference(8, 7)
    FINGER_BIN[1] = segment_abs_difference(12, 11)
    FINGER_BIN[2] = segment_abs_difference(16, 15)
    FINGER_BIN[3] = segment_abs_difference(20, 19)


def finger_2_binary():
    binary = ''.join(FINGER_BIN)
    return int(binary[:: -1], 2)


def hud_text(cv2,img,fps,h, w):
    cv2.putText(img, str(int(fps)), (10, 70),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255))
    cv2.putText(img, f"{finger_2_binary()}", (int(w-100), h-20),
                cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), thickness=3)

    cv2.putText(img, f"{CONTROLLER[finger_2_binary()]}", (int(w/2-100), h-150),
                cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), thickness=3)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils
pTime = 0
cTime = 0
cap = cv2.VideoCapture(1)


finger_val = ''
while interface["open"] == True:
    time.sleep(0.4) #this value controlls fps
    interface = keyboard_GUI(interface)
    success, img = cap.read()
    h, w, c = img.shape
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    img = cv2.flip(img, 1)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                SEGMENT_POS[id] = lm
        SEGMENT_POS = originize_seg_zero(SEGMENT_POS)
        interface["palm_direction"] = palm_or_back()
        finger_binary_monitor()
        

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    


    # hud_text(cv2,img,fps,h,w)
    if finger_val is not finger_2_binary():
        finger_val = finger_2_binary()
        print(CONTROLLER[finger_2_binary()])
        if finger_val == 8:
            if int(input("would you like to quit? (1/0)")):
                break


    # if finger_val != finger_2_binary():
    #     finger_val= finger_2_binary()   
    #     print(finger_val)
    #     if finger_val == 7:
    #         ser.write("on".encode())
    #         print("LED ON")
    #     if finger_val == 0:
    #         print("LED OFF")
    #         ser.write("off".encode())


    # cv2.imshow("image", img)

# ser.close()