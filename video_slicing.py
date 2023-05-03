import math
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from moviepy.editor import VideoFileClip

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

videopath = 'video_path' #path

cap = cv2.VideoCapture(videopath) 
clip = VideoFileClip(videopath)

width =cap.get(3)
height =cap.get(4)
TotalFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

framelist = []
AnklePosY = []


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
            ankleY = height - results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * height
        else:
            ankleY = 0
        AnklePosY.append(ankleY)
   
        if cv2.waitKey(5) & int(frame) == int(TotalFrame):
            break
            
Amp = 30 #Arithmetic mean parameter
Am_Y = []
cal_Y = 0

for i in range(Amp):
    cal_Y = cal_Y + AnklePosY[i]
for i in range(Amp, len(AnklePosY)):
    Am_Y.append(cal_Y / Amp)
    cal_Y = cal_Y - AnklePosY[i-Amp]
    cal_Y = cal_Y + AnklePosY[i]

Am_framelist = framelist[Amp:]

slicetime = []

for i in range(100,len(Am_framelist)-100):
    lowest = 1
    for j in range(1,100):
        if Am_Y[i] > Am_Y[i+j] or Am_Y[i] > Am_Y[i-j]:
            lowest = 0
            break;
    if lowest == 1:
        slicetime.append(Am_framelist[i])

fps=clip.fps
start_time = 0  
end_time = 0  
n=1

for i in range(len(slicetime)):
    end_time = slicetime[i]/fps
    if n <= 3: 
        clip.subclip(start_time, end_time).write_videofile(f'B_{n}.mp4') #write video
    elif n >= 4 and n <= 7:
        clip.subclip(start_time, end_time).write_videofile(f'R_{n-4}.mp4')
    elif n >= 8:
        clip.subclip(start_time, end_time).write_videofile(f'L_{n-7}.mp4')
    start_time = (slicetime[i]+1)/fps
    n+=1
end_time = clip.duration
if n >= 8:
    clip.subclip(start_time, end_time).write_videofile(f'L_{n-7}.mp4') #write video
else: 
     clip.subclip(start_time, end_time).write_videofile(f'L_{n}.mp4')
