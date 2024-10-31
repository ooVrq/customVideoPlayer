import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip

class VideoThumbnails:
    def __init__(self, root, video_folder):
        self.root = root
        self.root.geometry("800x600")

        self.thumbnail_frame = ttk.Frame(self.root)
        self.thumbnail_frame.pack(pady=10)

        self.load_thumbnails(video_folder)

    def load_thumbnails(self, video_folder):
        files = [f for f in os.listdir(video_folder) if f.lower().endswith((".mp4", ".mkv", ".avi"))]

        for i, video_file in enumerate(files):

            video_path = os.path.join(video_folder, video_file)
            thumbnail = self.create_thumbnail(video_path)

            col = i % 4
            row = i // 4
            label = ttk.Label(self.thumbnail_frame, image=thumbnail)
            label.image = thumbnail
            label.grid(row=row, column=col, padx=10, pady=10)

            title_label = tk.Label(self.thumbnail_frame, text=video_file[:-4])
            title_label.grid(row=row + 1, column=col, padx=10, pady=5)

    def create_thumbnail(self, video_path):
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(1)
        thumbnail = Image.fromarray(frame)
        thumbnail.thumbnail((150, 100))
        return ImageTk.PhotoImage(thumbnail)

def main():
    root = tk.Tk()
    folder_path = r"F:\Shows\Blend S"
    new_window = VideoThumbnails(root, folder_path)
    root.mainloop()

main()