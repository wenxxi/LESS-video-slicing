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

subjectpath = '/Volumes/Transcend/data/2020醒吾華橋 科技部/DT022-f/' 
videopath = subjectpath + 'DT022 t1 後測 側.MP4'
folderpath = 'DT022_t1_S_1_2/'
txtpath = subjectpath + folderpath + 'log.txt'

cap = cv2.VideoCapture(videopath) 
clip = VideoFileClip(videopath)

width =cap.get(3)
height =cap.get(4)
TotalFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

framelist = []
RAnklePosX = []
LAnklePosX = []


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
        if int(frame) == 1 and results.pose_landmarks:
            firstX = width - results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * width #以右邊界為0
        else:
            firstX = 5000 #使默認左邊為0
        if firstX < 2500 and results.pose_landmarks:
            LankleX = width - results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * width #以右邊界為0
            RankleX = width - results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * width
        elif results.pose_landmarks:
            LankleX = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * width #以左邊界為0
            RankleX = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * width
        else:
            LankleX = 0
            RankleX = 0
        LAnklePosX.append(LankleX)
        RAnklePosX.append(RankleX)
   
        if cv2.waitKey(5) & int(frame) == int(TotalFrame):
            break
            
Amp = 30 #Arithmetic mean parameter
LAm_X = []
RAm_X = []
Lcal_X = 0
Rcal_X = 0
for i in range(Amp):
    Lcal_X = Lcal_X + LAnklePosX[i]
    Rcal_X = Rcal_X + RAnklePosX[i]
for i in range(Amp, len(LAnklePosX)):
    LAm_X.append(Lcal_X / Amp)
    RAm_X.append(Rcal_X / Amp)
    Lcal_X = Lcal_X - LAnklePosX[i-Amp]
    Lcal_X = Lcal_X + LAnklePosX[i]
    Rcal_X = Rcal_X - RAnklePosX[i-Amp]
    Rcal_X = Rcal_X + RAnklePosX[i]

Am_framelist = framelist[Amp:]

plt.figure()
plt.plot(Am_framelist, RAm_X)
plt.plot(Am_framelist, LAm_X)
plt.savefig(subjectpath + folderpath + 'ankle_trajectory.png')

Ldx_list = [0]
Rdx_list = [0]
for i in range(1,len(Am_framelist)):
    Rdx = RAm_X[i]-RAm_X[i-1]
    Ldx = LAm_X[i]-LAm_X[i-1]
    Rdx_list.append(Rdx)
    Ldx_list.append(Ldx)
plt.figure()
plt.plot(Am_framelist, Rdx_list)
plt.plot(Am_framelist, Ldx_list)
plt.savefig(subjectpath + folderpath + 'delta_ankle.png')

#腳踝
Rslice_frame = []
Lslice_frame = []
label = []

# Rmaxframe = 1
# Rmax = 0
# for i in range(1, 85):
#     if Rdx_list[i] > Rmax:
#         Rmax = Rdx_list[i]
#         Rmaxframe = i
# Rslice_frame.append(Am_framelist[Rmaxframe])
# Lmaxframe = 1
# Lmax = 0
# for i in range(1, 85):
#     if Ldx_list[i] > Lmax:
#         Lmax = Ldx_list[i]
#         Lmaxframe = i
# Lslice_frame.append(Am_framelist[Lmaxframe])

for i in range(85,len(Am_framelist)-85):
    Rhighest = 1
    Lhighest = 1
    for j in range(1,85):
        if RAm_X[i] <= 1000 or Rdx_list[i] <= Rdx_list[i+j] or Rdx_list[i] <= Rdx_list[i-j]:
            Rhighest = 0
            break
    if Rhighest == 1:
        Rslice_frame.append(Am_framelist[i])
        
    for k in range(1,85):
        if LAm_X[i] <= 1000 or Ldx_list[i] <= Ldx_list[i+k] or Ldx_list[i] <= Ldx_list[i-k]:
            Lhighest = 0
            break
    if Lhighest == 1:
        Lslice_frame.append(Am_framelist[i])
Rmaxframe = len(Am_framelist)-85
Rmax = 0
for i in range(len(Am_framelist)-85, len(Am_framelist)):
    if Rdx_list[i] > Rmax:
        Rmax = Rdx_list[i]
        Rmaxframe = i
Rslice_frame.append(Am_framelist[Rmaxframe])

Lmaxframe = len(Am_framelist)-85
Lmax = 0
for i in range(len(Am_framelist)-85, len(Am_framelist)):
    if Ldx_list[i] > Lmax:
        Lmax = Ldx_list[i]
        Lmaxframe = i
Lslice_frame.append(Am_framelist[Lmaxframe])
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