import math
from re import L
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from moviepy.editor import VideoFileClip

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

videopath = '/Volumes/Transcend/data/2020醒吾華橋 科技部/DT001-f/DT001 t1 前測 前.MP4' #path
cap = cv2.VideoCapture(videopath) 
clip = VideoFileClip(videopath)

width =cap.get(3)
height =cap.get(4)
TotalFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

framelist = []
RAnklePosY = []
LAnklePosY = []
LKneePosY = []
RKneePosY = []


with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    while(True):
        success, image = cap.read()
        if not success:
            continue
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        # Draw the pose annotation on the image.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        framelist.append(frame)
        if results.pose_landmarks:
            RankleY = height - results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * height 
            LankleY = height - results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * height
            RkneeY = height - results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y * height
            LkneeY = height - results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y * height
        else:
            RankleY = 0
            LankleY = 0
            RkneeY = 0
            LkneeY = 0
        RAnklePosY.append(RankleY)
        LAnklePosY.append(LankleY)
        LKneePosY.append(LkneeY)
        RKneePosY.append(RkneeY)
   
        if cv2.waitKey(5) & int(frame) == int(TotalFrame):
            break
            
Amp = 30 #Arithmetic mean parameter
RAm_Y = []
LAm_Y = []
RkAm_Y = []
LkAm_Y = []
Rcal_Y = 0
Lcal_Y = 0
Rkcal_Y = 0
Lkcal_Y = 0
for i in range(Amp):
    Rcal_Y = Rcal_Y + RAnklePosY[i]
    Lcal_Y = Lcal_Y + LAnklePosY[i]
    Rkcal_Y = Rkcal_Y + RKneePosY[i]
    Lkcal_Y = Lkcal_Y + LKneePosY[i]
for i in range(Amp, len(RAnklePosY)):
    RAm_Y.append(Rcal_Y / Amp)
    RkAm_Y.append(Rkcal_Y / Amp)
    LAm_Y.append(Lcal_Y / Amp)
    LkAm_Y.append(Lkcal_Y / Amp)
    Rcal_Y = Rcal_Y - RAnklePosY[i-Amp]
    Rcal_Y = Rcal_Y + RAnklePosY[i]
    Lcal_Y = Lcal_Y - LAnklePosY[i-Amp]
    Lcal_Y = Lcal_Y + LAnklePosY[i]
    Rkcal_Y = Rkcal_Y - RKneePosY[i-Amp]
    Rkcal_Y = Rkcal_Y + RKneePosY[i]
    Lkcal_Y = Lkcal_Y - LKneePosY[i-Amp]
    Lkcal_Y = Lkcal_Y + LKneePosY[i]

Am_framelist = framelist[Amp:]

difR = []
difL = []
for i in range(0, len(Am_framelist)):
    difR.append(RkAm_Y[i] - RAm_Y[i])
    difL.append(LkAm_Y[i] - LAm_Y[i])

Ldy_list = [0]
Rdy_list = [0]
for i in range(1,len(Am_framelist)):
    Rdy = RAm_Y[i]-RAm_Y[i-1]
    Ldy = LAm_Y[i]-LAm_Y[i-1]
    Rdy_list.append(Rdy)
    Ldy_list.append(Ldy)

#膝蓋-腳踝
RKslice_frame = []
LKslice_frame = []
for i in range(100,len(Am_framelist)-100):
    RKlowest = 1
    LKlowest = 1
    for j in range(1,100): 
        if difR[i] >= 100 or difR[i] >= difR[i+j] or difR[i] >= difR[i-j]:
            RKlowest = 0
            break
    if RKlowest == 1:
        RKslice_frame.append(Am_framelist[i])
        
    for k in range(1,100):
        if difL[i] >= 100 or difL[i] >= difL[i+k] or difL[i] >= difL[i-k]:
            LKlowest = 0
            break
    if LKlowest == 1:
        LKslice_frame.append(Am_framelist[i])
for i in range(len(Am_framelist)-100, len(Am_framelist)):
    RKlowest = 1
    LKlowest = 1
    for j in range(len(Am_framelist)-i):
        if difR[i] >= 100 or difR[i] >= difR[i+j] or difR[i] >= difR[i-j]:
            RKlowest = 0
            break
    if RKlowest == 1:
        RKslice_frame.append(Am_framelist[i])
    for k in range(len(Am_framelist)-i):
        if difL[i] >= 100 or difL[i] >= difL[i+k] or difL[i] >= difL[i-k]:
            LKlowest = 0
            break
    if LKlowest == 1:
        LKslice_frame.append(Am_framelist[i])
print("Left takeoff frame:", LKslice_frame)
print("Right takeoff frame:", RKslice_frame)

#move to here for screenshot
Kslice_frame = RKslice_frame + LKslice_frame
Kslice_frame.sort()
print("Unilateral takeoff frame:",Kslice_frame)

#腳踝
Rslice_frame = []
Lslice_frame = []
for i in range(100,len(Am_framelist)-100):
    Rlowest = 1
    Llowest = 1
    for j in range(1,100):
        if Rdy_list[i] >= -7 or Rdy_list[i] >= Rdy_list[i+j] or Rdy_list[i] >= Rdy_list[i-j]:
            Rlowest = 0
            break
    if Rlowest == 1:
        Rslice_frame.append(Am_framelist[i])
        
    for k in range(1,100):
        if Ldy_list[i] >= -7 or Ldy_list[i] >= Ldy_list[i+k] or Ldy_list[i] >= Ldy_list[i-k]:
            Llowest = 0
            break
    if Llowest == 1:
        Lslice_frame.append(Am_framelist[i])
for i in range(len(Am_framelist)-100, len(Am_framelist)):
    Rlowest = 1
    Llowest = 1
    for j in range(len(Am_framelist)-i):
        if Rdy_list[i] >= -7 or Rdy_list[i] >= Rdy_list[i+j] or Rdy_list[i] >= Rdy_list[i-j]:
            Rlowest = 0
            break
    if Rlowest == 1 and Am_framelist[i] - Rslice_frame[-1] > 100:
        Rslice_frame.append(Am_framelist[i])
        
    for k in range(len(Am_framelist)-i):
        if Ldy_list[i] >= -7 or Ldy_list[i] >= Ldy_list[i+k] or Ldy_list[i] >= Ldy_list[i-k]:
            Llowest = 0
            break
    if Llowest == 1 and Am_framelist[i] - Lslice_frame[-1] > 100:
        Lslice_frame.append(Am_framelist[i])
print("Slice frame calculated by the right ankle:", Rslice_frame)
print("Slice frame calculated by the left ankle::", Lslice_frame) 

#slice_frame製作
if len(Rslice_frame) <= len(Lslice_frame):
    double_last = len(Rslice_frame) - len(Kslice_frame)
    slice_frame = Rslice_frame[0 : double_last]
else:
    double_last = len(Lslice_frame) - len(Kslice_frame)
    slice_frame = Lslice_frame[0 : double_last]
for i in Kslice_frame:
    slice_frame.append(i)
slice_frame.sort()
print("Total sliced frame:",slice_frame)
#print("double_last:",double_last)

#slice the video
fps=clip.fps
n=1
for i in range(len(slice_frame)):
    if i < double_last:
        start_frame = slice_frame[i]-40
        end_frame = start_frame + 83
    else:
        start_frame = slice_frame[i]-55
        end_frame = start_frame + 83
    start_time = start_frame / fps
    print("start",start_time)
    end_time = end_frame / fps
    print("end",end_time)
    clip.subclip(start_time, end_time).write_videofile(f'/Volumes/Transcend/data/2020醒吾華橋 科技部/DT001-f/v2/{n}.mp4')
    n+=1
