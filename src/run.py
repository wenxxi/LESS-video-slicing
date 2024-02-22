import cv2
from moviepy.editor import VideoFileClip
from utils import *
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='LESS-video-sling')
    parser.add_argument('videopath', type=str, help='Path to the input video file')
    parser.add_argument('label', type=str, choices=['F', 'S'], help='Label for the type of processing (F for front and S for side)')
    parser.add_argument('folderpath', type=str, help='Path to the folder for saving output files')
    return parser.parse_args()

def main():
    args = parse_arguments()

    videopath = args.videopath
    label = args.label
    folderpath = args.folderpath
    txtpath = folderpath + 'log.txt'

    cap = cv2.VideoCapture(videopath) 
    clip = VideoFileClip(videopath)
    width = cap.get(3)
    height = cap.get(4)
    TotalFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    if label == 'F':
        framelist, RAnklePosY, LAnklePosY = front_view(cap, height, TotalFrame)
        RAm_Y, LAm_Y, Am_framelist = smoothing(framelist, RAnklePosY, LAnklePosY)
        Ldy_list, Rdy_list = calculate_slope(RAm_Y, LAm_Y, Am_framelist)
        Kslice_frame = front_takeoff(Rdy_list, Ldy_list, Am_framelist)
    elif label == 'S':
        framelist, RAnklePosX, LAnklePosX = side_view(cap, height, TotalFrame)
        RAm_X, LAm_X, Am_framelist = smoothing(framelist, RAnklePosX, LAnklePosX)
        Ldx_list, Rdx_list = calculate_slope(RAm_X, LAm_X, Am_framelist)
        Kslice_frame = side_takeoff(RAm_X, Rdx_list, LAm_X, Ldx_list, Am_framelist)

    frame_txt(txtpath, Kslice_frame)
    slice(clip, Kslice_frame, TotalFrame, folderpath)

    cap.release()

if __name__ == "__main__":
    main()




