import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Your CLI description here')
    parser.add_argument('videopath', type=str, help='Path to the input video file')
    parser.add_argument('label', type=str, help='Label for the type of processing (F or S)')
    parser.add_argument('folderpath', type=str, help='Path to the folder for saving output files')
    return parser.parse_args()

def main():
    args = parse_arguments()
    return args

if __name__ == "__main__":
    main()