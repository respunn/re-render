import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from moviepy.editor import VideoFileClip
import threading

class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Bulk Video Compressor')
        self.geometry('700x290')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.processing_active = False  # Flag to track whether processing is active

        # Frame for input folder
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, fill='x', padx=20)
        self.input_folder_entry = ctk.CTkEntry(input_frame, placeholder_text="Select input folder", width=400)
        self.input_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(input_frame, text="Browse", command=self.browse_input_folder).pack(side='left', padx=10)

        # Frame for output folder
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(pady=10, fill='x', padx=20)
        self.output_folder_entry = ctk.CTkEntry(output_frame, placeholder_text="Select output folder", width=400)
        self.output_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(output_frame, text="Browse", command=self.browse_output_folder).pack(side='left', padx=10)

        # Frame for bitrate entry and combobox
        bitrate_frame = ctk.CTkFrame(self)
        bitrate_frame.pack(pady=10, fill='x', padx=20)
        self.bitrate_entry = ctk.CTkEntry(bitrate_frame, placeholder_text="Enter target bitrate", width=200)
        self.bitrate_entry.pack(side='left', fill='x', expand=True)
        bitrate_units = ['K', 'M']
        self.bitrate_unit_combobox = ctk.CTkOptionMenu(bitrate_frame, values=bitrate_units)
        self.bitrate_unit_combobox.pack(side='left', padx=10)
        self.bitrate_unit_combobox.set('K')

        # Entry for minimum size with label
        min_size_frame = ctk.CTkFrame(self)
        min_size_frame.pack(pady=10, fill='x', padx=20)
        self.min_size_entry = ctk.CTkEntry(min_size_frame, placeholder_text="Minimum size for processing (MB)", width=200)
        self.min_size_entry.pack(side='left', fill='x', expand=True)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.pack(pady=20, padx=20)

        ctk.CTkButton(self, text='Start Processing', command=self.threaded_process).pack(pady=10)

    def reduce_video_size(self, video_input_path, video_output_path, target_bitrate):
        video = VideoFileClip(video_input_path)
        video.write_videofile(video_output_path, bitrate=target_bitrate)

    def process_videos(self):
        input_folder = self.input_folder_entry.get()
        output_folder = self.output_folder_entry.get()
        bitrate = self.bitrate_entry.get()
        min_size = float(self.min_size_entry.get())
        target_bitrate = f"{bitrate}{self.bitrate_unit_combobox.get()}"
        video_files = [f for f in os.listdir(input_folder) if f.endswith((".mp4", ".avi", ".mov"))]
        total_videos = len(video_files)

        for index, filename in enumerate(video_files):
            if not self.processing_active:
                break  # Early exit if the process was halted
            self.process_video(input_folder, output_folder, filename, target_bitrate, min_size, index, total_videos)

        self.processing_active = False  # Reset processing flag

    def process_video(self, input_folder, output_folder, filename, target_bitrate, min_size, index, total_videos):
        current_input_path = os.path.join(input_folder, filename)
        file_size_mb = os.path.getsize(current_input_path) / (1024 * 1024)
        if file_size_mb > min_size:
            current_output_path = os.path.join(output_folder, f"compressed_{filename}")
            self.reduce_video_size(current_input_path, current_output_path, target_bitrate)
            print(f"Processed {filename}")
        else:
            print(f"Skipped {filename}, file size {file_size_mb:.2f} MB is not greater than {min_size} MB.")
        self.progress_bar.set((index + 1) / total_videos * 100)

    def on_close(self):
        if self.processing_active:
            if messagebox.askyesno("Exit", "Processing is still active. Are you sure you want to exit?"):
                self.processing_active = False  # Signal to stop processing
                self.destroy()  # Close the application
        else:
            self.destroy()

    def browse_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_entry.delete(0, tk.END)
            self.input_folder_entry.insert(0, folder_selected)

    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder_selected)

    def threaded_process(self):
        self.processing_active = True
        threading.Thread(target=self.process_videos, daemon=True).start()

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()
