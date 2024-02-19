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

subjectpath = '/Volumes/Transcend/data/2020醒吾華橋 科技部/DT001-f/' 
videopath = subjectpath + 'DT001 t1 前測 側.MP4'
folderpath = 'DT001_t1_S_1_1/'
txtpath = subjectpath + folderpath + 'log.txt'

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
        else:
            RankleY = 0
            LankleY = 0
        RAnklePosY.append(RankleY)
        LAnklePosY.append(LankleY)
   
        if cv2.waitKey(5) & int(frame) == int(TotalFrame):
            break
            
Amp = 30 #Arithmetic mean parameter
RAm_Y = []
LAm_Y = []
Rcal_Y = 0
Lcal_Y = 0

for i in range(Amp):
    Rcal_Y = Rcal_Y + RAnklePosY[i]
    Lcal_Y = Lcal_Y + LAnklePosY[i]
for i in range(Amp, len(RAnklePosY)):
    RAm_Y.append(Rcal_Y / Amp)
    LAm_Y.append(Lcal_Y / Amp)
    Rcal_Y = Rcal_Y - RAnklePosY[i-Amp]
    Rcal_Y = Rcal_Y + RAnklePosY[i]
    Lcal_Y = Lcal_Y - LAnklePosY[i-Amp]
    Lcal_Y = Lcal_Y + LAnklePosY[i]

Am_framelist = framelist[Amp:]

plt.figure()
plt.plot(Am_framelist, RAm_Y)
plt.plot(Am_framelist, LAm_Y)
plt.savefig(subjectpath + folderpath + 'ankle_trajectory.png')

Ldy_list = [0]
Rdy_list = [0]
for i in range(1,len(Am_framelist)):
    Rdy = RAm_Y[i]-RAm_Y[i-1]
    Ldy = LAm_Y[i]-LAm_Y[i-1]
    Rdy_list.append(Rdy)
    Ldy_list.append(Ldy)
plt.figure()
plt.plot(Am_framelist, Rdy_list)
plt.plot(Am_framelist, Ldy_list)
plt.savefig(subjectpath + folderpath + 'delta_ankle.png')

#腳踝
Rslice_frame = []
Lslice_frame = []
label = []
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
Rminframe = len(Am_framelist)-100
Rmin = 0
for i in range(len(Am_framelist)-100, len(Am_framelist)):
    if Rdy_list[i] < Rmin:
        Rmin = Rdy_list[i]
        Rminframe = i
Rslice_frame.append(Am_framelist[Rminframe])

Lminframe = len(Am_framelist)-100
Lmin = 0
for i in range(len(Am_framelist)-100, len(Am_framelist)):
    if Ldy_list[i] < Lmin:
        Lmin = Ldy_list[i]
        Lminframe = i
Lslice_frame.append(Am_framelist[Lminframe])
print("Slice frame calculated by the right ankle:", Rslice_frame)
print("Slice frame calculated by the left ankle::", Lslice_frame) 

#若左右frame差正負100內，取先發生的
Kslice_frame = []
i=0
j=0

while i < len(Lslice_frame) and j < len(Rslice_frame):
    if abs(Lslice_frame[i] - Rslice_frame[j]) <= 100:
        if Lslice_frame[i] <= Rslice_frame[j]:
            Kslice_frame.append(Lslice_frame[i])
            label.append("L")
        else:
            Kslice_frame.append(Rslice_frame[j])
            label.append("R")
        i += 1
        j += 1
    elif Lslice_frame[i] < Rslice_frame[j]:
        Kslice_frame.append(Lslice_frame[i])
        label.append("L")
        i += 1
    else:
        Kslice_frame.append(Rslice_frame[j])
        label.append("R")
        j += 1

print("total slice frame:", Kslice_frame)

with open(txtpath, 'w') as f:
    f.write(f"Slice frame calculated by the right ankle: {Rslice_frame}\n")
    f.write(f"Slice frame calculated by the left ankle: {Lslice_frame}\n")
    f.write(f"Total sliced frame: {Kslice_frame}\n")

fps=clip.fps
n=1
b=1
l=1
r=1
for i in range(len(Kslice_frame)):
    start_frame = Kslice_frame[i]- 40 
    if start_frame + 85 <= TotalFrame:
        end_frame = start_frame + 85
    else:
        end_frame = TotalFrame
    start_time = start_frame / fps
    print("start",start_time)
    end_time = end_frame / fps
    print("end",end_time)
    clip.subclip(start_time, end_time).write_videofile(subjectpath + folderpath + f'{n}.mp4')
    n+=1
    # if i <= 3:
    #     clip.subclip(start_time, end_time).write_videofile(subjectpath + folderpath + f'B{b}.mp4')
    #     b+=1
    # elif label[i] == "L":
    #     clip.subclip(start_time, end_time).write_videofile(subjectpath + folderpath + f'L{l}.mp4')
    #     l+=1
    # elif label[i] == "R":
    #     clip.subclip(start_time, end_time).write_videofile(subjectpath + folderpath + f'R{r}.mp4')
    #     r+=1