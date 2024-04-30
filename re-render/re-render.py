import os
from moviepy.editor import VideoFileClip

def reduce_video_size(video_input_path, video_output_path, target_bitrate):
    video = VideoFileClip(video_input_path)
    video.write_videofile(video_output_path, bitrate=target_bitrate)

def process_videos():
    directory_path = os.path.dirname(os.path.realpath(__file__))
    input_videos_path = os.path.join(directory_path, "input_videos")
    output_videos_path = os.path.join(directory_path, "output_videos")

    # Ensure output directory exists
    if not os.path.exists(output_videos_path):
        os.makedirs(output_videos_path)

    target_bitrate = input("Please enter the desired bitrate (e.g., '500k'): ")

    for filename in os.listdir(input_videos_path):
        if filename.endswith((".mp4", ".avi", ".mov")):  
            current_input_path = os.path.join(input_videos_path, filename)
            file_size_mb = os.path.getsize(current_input_path) / (1024 * 1024)  # Convert bytes to megabytes
            if file_size_mb > 50:  # Check if file is larger than 50 MB
                current_output_path = os.path.join(output_videos_path, f"compressed_{filename}")
                reduce_video_size(current_input_path, current_output_path, target_bitrate)
                print(f"Processed {filename}")
            else:
                print(f"Skipped {filename}, file size {file_size_mb:.2f} MB is not greater than 50 MB.")

process_videos()
