# LESS-video-slicing
## Introduction of LESS
The Landing Error Scoring System (LESS) is a quantitative assessment tool used in various fields, particularly in orthopedic surgery and sports medicine, to evaluate and score the quality of landings from jumps or other athletic maneuvers. The system typically assigns numerical scores to various aspects of a landing, such as knee flexion, trunk flexion, and overall stability. These scores are then aggregated to provide an overall assessment of the landing quality, with higher scores indicating poorer technique and increased risk of injury.
## Function
This tool is designed to streamline the process of extracting specific segments from entire test procedure videos. It offers automated functionality to precisely cut out desired sections from takeoffs to landings. 

# Tutorial
## Clone repository
```
git clone https://github.com/wenxxi/LESS-video-slicing.git
```
## Command
Choose "F" for a front view video and "S" for a side view video.
```
python less.py /path/to/video.mp4 {F,S} /path/to/output/
```
