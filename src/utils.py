import cv2
import mediapipe as mp

def process_video(videopath):
    cap = cv2.VideoCapture(videopath) 
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
    
    cap.release()
    return framelist, RAnklePosY, LAnklePosY, LKneePosY, RKneePosY


def smoothing(framelist, RAnklePosY, LAnklePosY, LKneePosY, RKneePosY, Amp = 30):
    RAm_Y, LAm_Y, RkAm_Y, LkAm_Y = [], [], [], []
    Rcal_Y, Lcal_Y, Rkcal_Y, Lkcal_Y = 0, 0, 0, 0
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
    return RAm_Y, LAm_Y, RkAm_Y, LkAm_Y, Am_framelist

