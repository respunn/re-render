import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from moviepy.editor import VideoFileClip
import threading

def reduce_video_size(video_input_path, video_output_path, target_bitrate):
    video = VideoFileClip(video_input_path)
    video.write_videofile(video_output_path, bitrate=target_bitrate)

def process_videos(input_folder, output_folder, target_bitrate, min_size, progress_callback):
    video_files = [f for f in os.listdir(input_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    total_videos = len(video_files)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, filename in enumerate(video_files):
        current_input_path = os.path.join(input_folder, filename)
        file_size_mb = os.path.getsize(current_input_path) / (1024 * 1024)  # Convert bytes to megabytes
        if file_size_mb > min_size:
            current_output_path = os.path.join(output_folder, f"compressed_{filename}")
            full_bitrate = f"{target_bitrate}{bitrate_unit_combobox.get()}"
            reduce_video_size(current_input_path, current_output_path, full_bitrate)
            print(f"Processed {filename}")
        else:
            print(f"Skipped {filename}, file size {file_size_mb:.2f} MB is not greater than {min_size} MB.")
        progress_callback(index + 1, total_videos)

def update_progress(current, total):
    progress_var.set(current / total * 100)
    progress_bar.update()

def browse_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_selected)

def browse_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_selected)

def threaded_process():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    bitrate = bitrate_entry.get()
    min_size = float(min_size_entry.get())
    threading.Thread(target=process_videos, args=(input_folder, output_folder, bitrate, min_size, update_progress)).start()

app = tk.Tk()
app.title('Video Compressor')

tk.Label(app, text='Input Folder:').grid(row=0, column=0)
input_folder_entry = tk.Entry(app, width=50)
input_folder_entry.grid(row=0, column=1)
tk.Button(app, text="Browse", command=browse_input_folder).grid(row=0, column=2)

tk.Label(app, text='Output Folder:').grid(row=1, column=0)
output_folder_entry = tk.Entry(app, width=50)
output_folder_entry.grid(row=1, column=1)
tk.Button(app, text="Browse", command=browse_output_folder).grid(row=1, column=2)

tk.Label(app, text='Target Bitrate:').grid(row=2, column=0)
bitrate_entry = tk.Entry(app, width=15)
bitrate_entry.grid(row=2, column=1, sticky='w')

bitrate_units = ['K', 'M']  # Define bitrate units
bitrate_unit_combobox = ttk.Combobox(app, values=bitrate_units, width=3)
bitrate_unit_combobox.grid(row=2, column=1)
bitrate_unit_combobox.current(0)  # Set default selection

tk.Label(app, text='Min Size for Processing (MB):').grid(row=3, column=0)
min_size_entry = tk.Entry(app, width=20)
min_size_entry.grid(row=3, column=1)

progress_var = tk.DoubleVar()  # Variable to track progress
progress_bar = ttk.Progressbar(app, length=300, variable=progress_var, maximum=100)
progress_bar.grid(row=4, column=1, sticky='we')

tk.Button(app, text='Start Processing', command=threaded_process).grid(row=5, column=1)

app.mainloop()
