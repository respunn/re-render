import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from moviepy.editor import VideoFileClip
import threading
import re

class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Bulk Video Compressor')
        self.geometry('700x340')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()
        self.processing_active = False

    def create_widgets(self):
        # Input Folder Frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, fill='x', padx=20)
        self.input_folder_entry = ctk.CTkEntry(input_frame, placeholder_text="Select input folder", width=400)
        self.input_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(input_frame, text="Browse", command=self.browse_input_folder).pack(side='left', padx=(10,0))

        # Output Folder Frame
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(pady=10, fill='x', padx=20)
        self.output_folder_entry = ctk.CTkEntry(output_frame, placeholder_text="Select output folder", width=400)
        self.output_folder_entry.pack(side='left', fill='x', expand=True)
        ctk.CTkButton(output_frame, text="Browse", command=self.browse_output_folder).pack(side='left', padx=(10,0))

        # Bitrate Entry and Combobox
        bitrate_frame = ctk.CTkFrame(self)
        bitrate_frame.pack(pady=10, fill='x', padx=20)
        self.bitrate_entry = ctk.CTkEntry(bitrate_frame, placeholder_text="Enter target bitrate", width=200)
        self.bitrate_entry.pack(side='left', fill='x', expand=True)
        self.bitrate_entry.bind('<KeyRelease>', self.filter_numeric_input)

        self.bitrate_unit_combobox = ctk.CTkOptionMenu(bitrate_frame, values=['Kbps', 'Mbps'], command=None)
        self.bitrate_unit_combobox.pack(side='left', padx=(10,0))
        self.bitrate_unit_combobox.set("Mbps")

        # Minimum Size Entry
        min_size_frame = ctk.CTkFrame(self)
        min_size_frame.pack(pady=10, fill='x', padx=20)
        self.min_size_entry = ctk.CTkEntry(min_size_frame, placeholder_text="Minimum size for processing (MB)", width=200)
        self.min_size_entry.pack(side='left', fill='x', expand=True)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.pack(pady=20, padx=20)

        # Control Buttons
        ctk.CTkButton(self, text='Start Compressing', command=self.start_threaded_process).pack(pady=10)
        self.stop_button = ctk.CTkButton(self, text='Force Stop', command=self.confirm_stop, state='disabled', fg_color='red', hover_color="darkred")
        self.stop_button.pack(pady=10)

    def filter_numeric_input(self, event):
        entry = event.widget
        text = re.sub('[^0-9]', '', entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def browse_input_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_folder_entry.delete(0, tk.END)
            self.input_folder_entry.insert(0, folder_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder_path)

    def start_threaded_process(self):
        self.processing_active = True
        self.stop_button.configure(state='normal')
        thread = threading.Thread(target=self.process_videos, daemon=True)
        thread.start()

    def process_videos(self):
        input_folder = self.input_folder_entry.get()
        output_folder = self.output_folder_entry.get()
        bitrate = self.bitrate_entry.get() + self.bitrate_unit_combobox.get()
        min_size = float(self.min_size_entry.get())

        video_files = [f for f in os.listdir(input_folder) if f.endswith((".mp4", ".avi", ".mov"))]
        total_videos = len(video_files)

        for index, filename in enumerate(video_files):
            if not self.processing_active:
                break
            video_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"compressed_{filename}")
            file_size_mb = os.path.getsize(video_path) / (1024 ** 2)  # Convert bytes to MB

            if file_size_mb > min_size:
                self.compress_video(video_path, output_path, bitrate)
                self.update_progress_bar(index + 1, total_videos)
                print(f"Processed {filename}")
            else:
                print(f"Skipped {filename} due to insufficient size; {file_size_mb:.2f} MB is not greater than {min_size} MB.")

        self.processing_complete()

    def compress_video(self, input_path, output_path, bitrate):
        """Compresses a single video file to the specified bitrate."""
        try:
            video_clip = VideoFileClip(input_path)
            video_clip.write_videofile(output_path, bitrate=bitrate)
            video_clip.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compress video {os.path.basename(input_path)}: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)  # Clean up partially written files

    def update_progress_bar(self, current, total):
        """Updates the progress bar based on the current task index and total tasks."""
        progress = (current / total) * 100
        self.progress_bar.set(progress)
        self.update_idletasks()  # Force update of GUI elements

    def processing_complete(self):
        """Resets the UI and internal states after processing is complete."""
        self.processing_active = False
        self.stop_button.configure(state='disabled', fg_color='gray', hover_color='gray')
        self.progress_bar.set(0)
        messagebox.showinfo("Complete", "Video processing completed.")

    def confirm_stop(self):
        """Prompt the user to confirm if they want to forcibly stop the processing."""
        if self.processing_active:
            response = messagebox.askyesno("Force Stop", "Processing is active. Are you sure you want to stop?")
            if response:
                self.force_stop()

    def force_stop(self):
        """Forcibly stops the video processing."""
        self.processing_active = False
        print("Processing has been forcibly stopped.")

    def on_close(self):
        """Handler for the window close event."""
        if self.processing_active:
            response = messagebox.askyesno("Exit", "Processing is still active. Are you sure you want to exit?")
            if response:
                self.force_stop()
        self.destroy()

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()