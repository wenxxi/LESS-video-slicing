import cv2
import mediapipe as mp
from moviepy.editor import VideoFileClip

# 可合併？
def front_view(cap, height, TotalFrame):
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

def side_view(cap, width, TotalFrane):
    framelist, RAnklePosX, LAnklePosX = [], [], []

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

    cap.release()
    return framelist, RAnklePosX, LAnklePosX

def smoothing(framelist, RAnklePos, LAnklePos, Amp = 30): #front: Y, side: X
    RAm, LAm = [], []
    Rcal, Lcal = [], []
    for i in range(Amp):
        Rcal = Rcal + RAnklePos[i]
        Lcal = Lcal + LAnklePos[i]
    for i in range(Amp, len(RAnklePos)):
        RAm.append(Rcal / Amp)
        LAm.append(Lcal / Amp)
        Rcal = Rcal - RAnklePos[i-Amp]
        Rcal = Rcal + RAnklePos[i]
        Lcal = Lcal - LAnklePos[i-Amp]
        Lcal = Lcal + LAnklePos[i]

    Am_framelist = framelist[Amp:]
    return RAm, LAm, Am_framelist

# 以下兩者可合併為上
# def front_smoothing(framelist, RAnklePosY, LAnklePosY, Amp = 30):
#     RAm_Y, LAm_Y = [], []
#     Rcal_Y, Lcal_Y = 0, 0
#     for i in range(Amp):
#         Rcal_Y = Rcal_Y + RAnklePosY[i]
#         Lcal_Y = Lcal_Y + LAnklePosY[i]
#     for i in range(Amp, len(RAnklePosY)):
#         RAm_Y.append(Rcal_Y / Amp)
#         LAm_Y.append(Lcal_Y / Amp)
#         Rcal_Y = Rcal_Y - RAnklePosY[i-Amp]
#         Rcal_Y = Rcal_Y + RAnklePosY[i]
#         Lcal_Y = Lcal_Y - LAnklePosY[i-Amp]
#         Lcal_Y = Lcal_Y + LAnklePosY[i]

#     Am_framelist = framelist[Amp:]
#     return RAm_Y, LAm_Y, Am_framelist

# def side_smoothing(framelist, RAnklePosX, LAnklePosX, Amp = 30):
#     LAm_X, RAm_X = [], []   
#     Lcal_X, Rcal_X = 0, 0
#     for i in range(Amp):
#         Lcal_X = Lcal_X + LAnklePosX[i]
#         Rcal_X = Rcal_X + RAnklePosX[i]
#     for i in range(Amp, len(LAnklePosX)):
#         LAm_X.append(Lcal_X / Amp)
#         RAm_X.append(Rcal_X / Amp)
#         Lcal_X = Lcal_X - LAnklePosX[i-Amp]
#         Lcal_X = Lcal_X + LAnklePosX[i]
#         Rcal_X = Rcal_X - RAnklePosX[i-Amp]
#         Rcal_X = Rcal_X + RAnklePosX[i]

#     Am_framelist = framelist[Amp:]
#     return RAm_X, LAm_X, Am_framelist


def calculate_slope(RAm, LAm, Am_framelist): #front: Y, side: X
    Ld_list, Rd_list = [0], [0]
    for i in range(1,len(Am_framelist)):
        Rd = RAm[i]-RAm[i-1]
        Ld = LAm[i]-LAm[i-1]
        Rd_list.append(Rd)
        Ld_list.append(Ld)
    return Ld_list, Rd_list

# side view:
# Ldx_list = [0]
# Rdx_list = [0]
# for i in range(1,len(Am_framelist)):
#     Rdx = RAm_X[i]-RAm_X[i-1]
#     Ldx = LAm_X[i]-LAm_X[i-1]
#     Rdx_list.append(Rdx)
#     Ldx_list.append(Ldx)

def front_takeoff(Rdy_list, Ldy_list, Am_framelist):
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

def side_takeoff(RAm_X, Rdx_list, LAm_X, Ldx_list, Am_framelist):
    Rslice_frame, Lslice_frame, Kslice_frame = [], [], []
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
