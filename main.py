import cv2
import mediapipe as mp
import rtmidi
from rtmidi.midiconstants import (CONTROL_CHANGE)
import time
import numpy as np


midiout=rtmidi.MidiOut()
midiout.open_port(2)

hands=mp.solutions.hands
mphands=hands.Hands(static_image_mode=False,max_num_hands=2)

draw=mp.solutions.drawing_utils

cam=cv2.VideoCapture(0)

tempo=0.2
def convert_range(value, in_min, in_max, out_min, out_max):
    l_span = in_max - in_min
    r_span = out_max - out_min
    scaled_value = (value - in_min) / l_span
    scaled_value = out_min + (scaled_value * r_span)
    return np.round(scaled_value)

def send_notes(pitch=60,repeat=1):
    for _ in range(repeat):
        note_on=[0x90,pitch,112]
        note_off=[0x80,pitch,0]
        midiout.send_message(note_on)
        time.sleep(tempo)
        midiout.send_message(note_off)
def send_cc(cc=0,value=0):
    if value>0:
        mod=([CONTROL_CHANGE | 0,cc,value])
        midiout.send_message(mod)

while True:
    statues,image=cam.read()

    image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    image=cv2.flip(image,1)

    results=mphands.process(image)

    if results.multi_hand_landmarks:
        h,w,c=image.shape
        for hands_params in results.multi_hand_landmarks:
            pink_x=hands_params.landmark[hands.HandLandmark.PINKY_TIP].x
            pink_y=hands_params.landmark[hands.HandLandmark.PINKY_TIP].y

            if pink_x*w< w//2:
                print('LEFT  CC_DATA')
                v1=convert_range(pink_y,1.0,0,0,127)
                send_cc(1,value=v1)

            if pink_x*w>w//2:
                print('RIGHT  MIDI_DATA')
                v2=convert_range(pink_y,1.0,-1.0,60,92)
                send_notes(v2,1)
        draw.draw_landmarks(image,hands_params,hands.HAND_CONNECTIONS)

    cv2.putText(image,str('Ragha'),(10,70),cv2.FONT_HERSHEY_PLAIN,2,(255,205,5),3)
    cv2.imshow('Python Project',image)


    cv2.waitKey(1)