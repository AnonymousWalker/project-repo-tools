import sys
import os
from tstudio2rc import convert, convertDir

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py [tstudio_file_path] [output_directory]")
        exit()

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if os.path.isdir(input_path):
        convertDir(input_path, output_dir)
    else:
        convert(input_path, output_dir)
    
    print("Done!")