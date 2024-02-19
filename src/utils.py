import cv2
import mediapipe as mp
from moviepy.editor import VideoFileClip

def process_video(cap, heigh, TotalFrame):
    framelist, RAnklePosY, LAnklePosY = [], [], []

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
    
    cap.release()
    return framelist, RAnklePosY, LAnklePosY


def smoothing(framelist, RAnklePosY, LAnklePosY, Amp = 30):
    RAm_Y, LAm_Y = [], []
    Rcal_Y, Lcal_Y = 0, 0
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
    return RAm_Y, LAm_Y, Am_framelist

def calculate_slope(RAm_Y, LAm_Y, Am_framelist):
    Ldy_list, Rdy_list = [0], [0]
    for i in range(1,len(Am_framelist)):
        Rdy = RAm_Y[i]-RAm_Y[i-1]
        Ldy = LAm_Y[i]-LAm_Y[i-1]
        Rdy_list.append(Rdy)
        Ldy_list.append(Ldy)
    return Ldy_list, Rdy_list

def takeoff_frame(Rdy_list, Ldy_list, Am_framelist):
    Rslice_frame, Lslice_frame, Kslice_frame = [], [], []
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

    i, j = 0, 0
    while i < len(Lslice_frame) and j < len(Rslice_frame):
        if abs(Lslice_frame[i] - Rslice_frame[j]) <= 100:
            if Lslice_frame[i] <= Rslice_frame[j]:
                Kslice_frame.append(Lslice_frame[i])
            else:
                Kslice_frame.append(Rslice_frame[j])
            i += 1
            j += 1
        elif Lslice_frame[i] < Rslice_frame[j]:
            Kslice_frame.append(Lslice_frame[i])
            i += 1
        else:
            Kslice_frame.append(Rslice_frame[j])
            j += 1 
    return Kslice_frame

def frame_txt(txtpath, Kslice_frame):
    with open(txtpath, 'w') as f:
        f.write(f"Total sliced frame: {Kslice_frame}\n")

def slice(clip, Kslice_frame, TotalFrame, folderpath):
    fps=clip.fps
    n=1
    for i in range(len(Kslice_frame)):
        start_frame = Kslice_frame[i]- 40 
        if start_frame + 85 <= TotalFrame:
            end_frame = start_frame + 85
        else:
            end_frame = TotalFrame
    start_time = start_frame / fps
    end_time = end_frame / fps
    clip.subclip(start_time, end_time).write_videofile(folderpath + f'{n}.mp4')
    n+=1
