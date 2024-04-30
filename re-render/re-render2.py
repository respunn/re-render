import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from moviepy.editor import VideoFileClip
import threading
import re
from io import StringIO

class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Bulk Video Compressor')
        self.geometry('700x340')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.processing_active = False  # Flag to track whether processing is active

        # Frame for input folder
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, fill='x', padx=20)
        self.input_folder_entry = ctk.CTkEntry(input_frame, placeholder_text="Select input folder", width=400)
        self.input_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(input_frame, text="Browse", command=self.browse_input_folder).pack(side='left', padx=(10,0))

        # Frame for output folder
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(pady=10, fill='x', padx=20)
        self.output_folder_entry = ctk.CTkEntry(output_frame, placeholder_text="Select output folder", width=400)
        self.output_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(output_frame, text="Browse", command=self.browse_output_folder).pack(side='left', padx=(10,0))

        # Frame for bitrate entry and combobox
        bitrate_frame = ctk.CTkFrame(self)
        bitrate_frame.pack(pady=10, fill='x', padx=20)
        
        self.bitrate_entry = ctk.CTkEntry(bitrate_frame, placeholder_text="Enter target bitrate", width=200)
        self.bitrate_entry.pack(side='left', fill='x', expand=True)
        
        # Bind key release event to filter non-numeric input
        self.bitrate_entry.bind('<KeyRelease>', self.filter_numeric_input)

        bitrate_units = ['K', 'M']
        self.bitrate_unit_combobox = ctk.CTkOptionMenu(bitrate_frame, values=bitrate_units)
        self.bitrate_unit_combobox.pack(side='left', padx=(10,0))
        self.bitrate_unit_combobox.set('M')

        # Entry for minimum size with label
        min_size_frame = ctk.CTkFrame(self)
        min_size_frame.pack(pady=10, fill='x', padx=20)
        self.min_size_entry = ctk.CTkEntry(min_size_frame, placeholder_text="Minimum size for processing (MB)", width=200)
        self.min_size_entry.pack(side='left', fill='x', expand=True)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.pack(pady=20, padx=20)

        # Start and stop buttons
        ctk.CTkButton(self, text='Start Compressing', command=self.threaded_process).pack(pady=10)
        self.stop_button = ctk.CTkButton(self, text='Force Stop', command=self.confirm_stop, fg_color='red', hover_color="darkred")
        self.stop_button.pack(pady=10)
        self.stop_button.configure(state='disabled')
        if self.stop_button.cget('state') == 'disabled':
            self.stop_button.configure(fg_color='gray', hover_color='gray')

    def filter_numeric_input(self, event):
        # Get current entry content and filter out non-digit characters
        current_text = event.widget.get()
        filtered_text = ''.join(filter(str.isdigit, current_text))
        if current_text != filtered_text:
            event.widget.delete(0, tk.END)
            event.widget.insert(0, filtered_text)

    def reduce_video_size(self, video_input_path, video_output_path, target_bitrate):
        video = VideoFileClip(video_input_path)
        video.write_videofile(video_output_path, bitrate=target_bitrate)

    def process_videos(self):
        try:
            input_folder = self.input_folder_entry.get()
            output_folder = self.output_folder_entry.get()
            bitrate = self.bitrate_entry.get()
            min_size = float(self.min_size_entry.get())
            target_bitrate = f"{bitrate}{self.bitrate_unit_combobox.get()}"
            video_files = [f for f in os.listdir(input_folder) if f.endswith((".mp4", ".avi", ".mov"))]
            total_videos = len(video_files)

            self.stop_button.configure(state='normal')
            if self.stop_button.cget('state') == 'normal':
                self.stop_button.configure(fg_color='red', hover_color='darkred')

            for index, filename in enumerate(video_files):
                if not self.processing_active:
                    break
                self.process_video(input_folder, output_folder, filename, target_bitrate, min_size, index, total_videos)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.processing_active = False
            self.stop_button.configure(g_color='gray', hover_color='gray', state='disabled')

    def process_video(self, input_folder, output_folder, filename, target_bitrate, min_size, index, total_videos):
        try:
            current_input_path = os.path.join(input_folder, filename)
            file_size_mb = os.path.getsize(current_input_path) / (1024 * 1024)
            if file_size_mb > min_size:
                current_output_path = os.path.join(output_folder, f"compressed_{filename}")
                self.reduce_video_size(current_input_path, current_output_path, target_bitrate)
                print(f"Processed {filename}")
            else:
                print(f"Skipped {filename}, file size {file_size_mb:.2f} MB is not greater than {min_size} MB.")
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to process {filename}: {e}")

    def browse_input_folder(self):
        try:
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.input_folder_entry.delete(0, tk.END)
                self.input_folder_entry.insert(0, folder_selected)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open directory: {e}")

    def browse_output_folder(self):
        try:
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.output_folder_entry.delete(0, tk.END)
                self.output_folder_entry.insert(0, folder_selected)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open directory: {e}")

    def on_close(self):
        if self.processing_active:
            if messagebox.askyesno("Exit", "Processing is still active. Are you sure you want to exit?"):
                self.processing_active = False
                self.destroy()
        else:
            self.destroy()

    def threaded_process(self):
        self.processing_active = True
        threading.Thread(target=self.process_videos, daemon=True).start()

    def confirm_stop(self):
        if self.processing_active == True:
            if messagebox.askyesno("Force Stop", "Are you sure you want to stop processing?"):
                self.force_stop()

    def force_stop(self):
        self.processing_active = False
        print("Processing has been forcibly stopped.")

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()
