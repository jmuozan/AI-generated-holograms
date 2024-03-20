import cv2
import numpy as np
import subprocess
import math
import os
import time


def flip_video(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Use 'XVID' if saving as .avi
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (frame_width, frame_height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Reached the end of the video or failed to read.")
            break
        
        flipped_frame = cv2.flip(frame, -1) # 0 for vertical, 1 for horizontal, -1 for both
        
        out.write(flipped_frame)
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Video has been flipped and saved.")

# Example usage
input_video_path = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4'
output_video_path = '/Users/jorgemuyo/Desktop/Challenge/video_flipped.mp4'
flip_video(input_video_path, output_video_path)





def create_hologram_layout(input_video_path, output_video_path):
    # Load the video
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    video_width, video_height = 2500, 2500  
    
    base_separation = 1000
    additional_push = 300 

    output_width = int(0.6 * video_width + 7 * base_separation + 10 * additional_push)
    output_height = int(0.6 * video_height + 7 * base_separation + 10 * additional_push)
    

    fourcc = cv2.VideoWriter_fourcc(*'avc1')  
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, output_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        small_frame = cv2.resize(frame, (video_width, video_height))
        
        hologram_frame = np.zeros((output_height, output_width, 3), dtype=np.uint8)
        
        positions = [
            # Top
            (output_width // 2 - video_width // 2, base_separation + additional_push),
            # Right
            (output_width - video_width - base_separation - additional_push, output_height // 2 - video_height // 2),
            # Bottom
            (output_width // 2 - video_width // 2, output_height - video_height - base_separation - additional_push),
            # Left
            (base_separation + additional_push, output_height // 2 - video_height // 2),
        ]
        
        for i, (pos_x, pos_y) in enumerate(positions):
            rotated_frame = np.rot90(small_frame, k=-i)
            hologram_frame[pos_y:pos_y+video_height, pos_x:pos_x+video_width] = rotated_frame
        
        out.write(hologram_frame)
    
    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()

input_video_path = output_video_path
initial_output_video_path = '/Users/jorgemuyo/Desktop/Challenge/VIDEO/hologram_video.mp4'

create_hologram_layout(input_video_path, initial_output_video_path)

# Define paths for the FFmpeg input (initial output) and final output video files
ffmpeg_input_path = initial_output_video_path
ffmpeg_output_path = '/Users/jorgemuyo/Desktop/Challenge/VIDEO/DEFINITIVE_HOLOGRAM.mp4'

# FFmpeg command to convert and resize the video
ffmpeg_command = [
    '/opt/homebrew/bin/ffmpeg',  # path of ffmpeg 
    '-i', ffmpeg_input_path,
    '-c:v', 'libx264',
    '-crf', '23',
    '-preset', 'veryfast',
    '-s', '2000x2000',  # Adjusted final video size
    ffmpeg_output_path
]

# Execute the FFmpeg command
subprocess.run(ffmpeg_command)

file_path = '/Users/jorgemuyo/Desktop/Challenge/VIDEO/DEFINITIVE_HOLOGRAM.mp4'
subprocess.call(['open', file_path])

