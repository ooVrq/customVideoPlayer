import tkinter as tk
import os
from tkinter import filedialog
import re
import tkinter.font as tkFont
import vlc
from tkinter import ttk
import sys
from PIL import Image, ImageTk
import time

class VLCApp:
    def __init__(self):
        # Initial root video frame
        self.root = tk.Tk()
        self.root.title("oVideo")
        x = 1000
        self.root.geometry(f"{x}x{int(x * 9/16)}")

        # Frame for the video creation
        self.create_video()
        # Frame overlay for the buttons
        self.create_button_overlay()

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.set_output()

        self.create_console()
        self.create_progress_bar()
        self.update_progress_bar()

        self.root.bind("<Configure>", self.on_resize)

        # On window close
        self.root.protocol("WM_DELETE_WINDOW", self.window_closed)

        self.last_update_time = 0
        self.enable_keybinds()
        self.console_input.bind("<FocusIn>", self.disable_keybinds)
        self.console_input.bind("<FocusOut>", self.enable_keybinds)

    def enable_keybinds(self, event=None):
        self.root.bind("<KeyPress-z>", self.show_buttons_keybind)
        self.root.bind("<KeyRelease-z>", self.hide_buttons_keybind)
        self.root.bind("<KeyPress-space>", self.pause_video)
        self.root.bind("<KeyPress-f>", self.set_fullscreen)
        self.root.bind("<KeyPress-m>", self.mute_audio_keybind)
        self.root.bind("<KeyPress-Escape>", self.unfullscreen_keybind)
        self.root.bind("<KeyPress-Left>", self.skip_time_keybind)
        self.root.bind("<KeyPress-Right>", self.skip_time_keybind)
        self.root.bind("<KeyPress-Up>", self.volume_keybind)
        self.root.bind("<KeyPress-Down>", self.volume_keybind)
        self.root.bind("<KeyPress-:>", self.show_console)
        self.console_input.unbind("<Return>")

    def disable_keybinds(self, event=None):
        self.root.unbind("<KeyPress-z>")
        self.root.unbind("<KeyRelease-z>")
        self.root.unbind("<KeyPress-space>")
        self.root.unbind("<KeyPress-f>")
        self.root.unbind("<KeyPress-m>")
        self.root.unbind("<KeyPress-Escape>")
        self.root.unbind("<KeyPress-Left>")
        self.root.unbind("<KeyPress-Right>")
        self.root.unbind("<KeyPress-Up>")
        self.root.unbind("<KeyPress-Down>")
        self.root.unbind("<KeyPress-:>")
        self.console_input.bind("<Return>", self.check_input)

    def window_closed(self):
        self.player.stop()
        self.player.release()
        self.root.destroy()
        sys.exit()

    def create_button_overlay(self):
        # Button Frame initialization
        self.button_color = "MediumPurple3"
        self.button_frame = tk.Frame(self.root, bg=self.button_color)  # Button frazme at the bottom
        #self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame for centering buttons
        self.center_frame = tk.Frame(self.button_frame, bg=self.button_color)
        self.center_frame.pack(side=tk.TOP, padx=10, pady=5)

        # Pause Button
        self.play_image = Image.open("icons/isplay.png")
        self.play_photo = ImageTk.PhotoImage(self.play_image)
        self.pause_image = Image.open("icons/ispause.png")
        self.pause_photo = ImageTk.PhotoImage(self.pause_image)
        self.pause_button = tk.Button(self.center_frame, image=self.play_photo, command=self.pause_video,)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Fullscreen Button
        self.fullscreen_image = Image.open("icons/fullscreen.png")
        self.fullscreen_photo = ImageTk.PhotoImage(self.fullscreen_image)
        self.toggle_fullscreen = tk.Button(self.center_frame, image=self.fullscreen_photo, command=self.set_fullscreen)
        self.toggle_fullscreen.pack(side=tk.LEFT, padx=5)

        # Volume Slider
        self.volume_label = tk.Label(self.center_frame, text="Volume: 0%")
        self.volume_slider = ttk.Scale(self.center_frame, from_=0, to=100, orient=tk.HORIZONTAL,  command=self.slider_volume)
        self.volume_label.pack(side=tk.LEFT, padx=5)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

    def create_console(self):
        font_style = tkFont.Font(family="Courier New", size=12, weight="normal")
        self.console_color = "navy"
        self.console_frame = tk.Frame(self.root, bg=self.console_color)

        self.colon_label = tk.Label(self.console_frame, font=font_style, bg=self.console_color, fg="white", text=":")
        self.colon_label.pack(side=tk.LEFT)
        self.console_input = tk.Entry(self.console_frame, bg=self.console_color, font=font_style, fg="white")
        self.console_input.pack(side=tk.LEFT, padx=(0, 10))

    def show_console(self, event=None):
        self.console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.console_input.focus_set()
        self.console_input.delete(0, tk.END)

    def check_input(self, event=None):
        input = self.console_input.get()
        print(input)
        if input == "pause":
            self.player.pause()
        if input == "play":
            self.player.play()
        if bool(re.fullmatch(r"\d{4}|\d{2}:\d{2}|\d{3}|\d{2}|\d{1}|\d{1}:\d{2}:\d{2}", input)):
            self.set_video_time(input)
        if input == "setfile" or input == "sf" or input == "next":
            self.play_video(input)
        self.console_frame.pack_forget()
        self.root.focus_set()

    def set_video_time(self, time):

        # XX:XX case
        if bool(re.fullmatch(r"\d{2}:\d{2}", time)):
            min, sec = time.split(":")

        # XXXX case
        elif bool(re.fullmatch(r"\d{4}", time)):
            min = time[:2]
            # test making changes
            sec = time[2:]

        # XXX case
        elif bool(re.fullmatch(r"\d{3}", time)):
            min = time

        # Valid second input check
        if int(sec) > 59:
            return

        # Time to ms
        time_ms = (int(min) * 60 + int(sec)) * 1000
        self.player.set_time(time_ms)

        print(min, sec)

    def create_video(self):
        self.video_frame = tk.Canvas(self.root, bg="purple")
        self.video_frame.pack(fill=tk.BOTH, expand=True)


    def set_output(self):
        self.player.set_hwnd(self.video_frame.winfo_id())

    def play_video(self, input):

        if self.player.is_playing():
            self.player.stop()

        if input == "sf" or input == "setfile":
            self.get_new_file()
        elif input == "next":
            self.play_next_file()

        file = self.vlc_instance.media_new(self.curr_path)

        self.player.set_media(file)
        self.player.play()
        self.volume_slider.set(self.player.audio_get_volume())

    def get_new_file(self):

        file_types = [("Video Files", "*.mp4;*.mkv;*.avi;*.mov"), ("Audio Files", "*.mp3;*.wav"),
                      ("All Files", "*.*")]
        self.curr_path = filedialog.askopenfilename(filetypes=file_types)

    def get_next_file(self):
        file_path = self.curr_path
        file_directory = os.path.dirname(file_path)
        files = sorted(os.listdir(file_directory))

        raw_file_name = os.path.basename(file_path)

        # Use a try to catch last file in folder error
        try:
            curr_index = files.index(raw_file_name)
            return os.path.join(file_directory, files[curr_index + 1])
        except IndexError:
            print("Last file in Folder")

    def play_next_file(self):
        path = self.get_next_file()

        if self.player.is_playing():
            self.player.stop()

        new_media_obj = self.vlc_instance.media_new(path)

        self.player.set_media(new_media_obj)
        self.player.play()

    def create_progress_bar(self):
        self.progress_frame = tk.Frame(self.button_frame, bg=self.button_color, height=30)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.curr_time = tk.Label(self.progress_frame, text="00:00", bg=self.button_color)
        self.curr_time.pack(side=tk.LEFT, padx=(0, 5))

        self.total_time = tk.Label(self.progress_frame, text="00:00", bg=self.button_color)
        self.total_time.pack(side=tk.RIGHT, padx=(5, 0))

        self.progress_bar = tk.Canvas(self.progress_frame, bg="lightgray", height=20)
        self.progress_bar.pack(fill=tk.BOTH, expand=True)

        self.bg_color = "lightgray"
        self.progress_bg = self.progress_bar.create_rectangle(0, 0, 0, 20, fill=self.bg_color, outline="")

        self.fg_color = "blue"
        self.progress_fg = self.progress_bar.create_rectangle(0, 0, 0, 20, fill=self.fg_color, outline="")

        self.progress_bar.bind("<Button-1>", self.set_bar_time)
        self.progress_bar.bind("<B1-Motion>", self.drag_time)



    def update_progress_bar(self):
        current_time = self.player.get_time()
        total_time = self.player.get_length()

        canvas_width = self.progress_bar.winfo_width()

        if total_time > 0:
            percent_complete = (current_time / total_time) * canvas_width
            self.progress_bar.coords(self.progress_fg, 0, 0, percent_complete, 20)
            self.curr_time.config(text=self.format_time(current_time))
            self.total_time.config(text=self.format_time(total_time))
        else:
            self.progress_bar.coords(self.progress_fg, 0, 0, 0, 20)

        self.root.after(1000, self.update_progress_bar)

    def format_time(self, time):
        total_seconds = time // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def on_resize(self, event):
        self.update_progress_bar()


    def set_bar_time(self, event):
        bar_length = self.progress_bar.winfo_width()
        click_x = event.x
        total_time = self.player.get_length()

        if total_time > 0:
            percent = click_x / bar_length
            new_time = int(percent * total_time)
            self.progress_bar.coords(self.progress_fg, 0, 0, click_x, 20)
            self.player.set_time(new_time)

    def drag_time(self, event):
        bar_length = self.progress_bar.winfo_width()
        click_x = event.x
        total_time = self.player.get_length()

        if total_time > 0:
            percent = click_x / bar_length
            new_time = int(percent * total_time)

            self.progress_bar.coords(self.progress_fg, 0, 0, click_x, 20)

            current_time = time.time()
            if current_time - self.last_update_time > 0.1:
                self.last_update_time = current_time
                self.player.set_time(new_time)

    def pause_video(self, event=None):
        if self.player.is_playing():
            self.pause_button.config(image=self.pause_photo)
            self.player.pause()
        else:
            self.pause_button.config(image=self.play_photo)
            self.player.pause()


    def set_fullscreen(self, event=None):
        fullscreen_state = self.player.get_fullscreen()
        print(fullscreen_state)
        self.player.set_fullscreen(not fullscreen_state)
        self.root.attributes("-fullscreen", not fullscreen_state)

    """def toggle_buttons_keybind(self, event=None):
        if self.button_frame.winfo_ismapped():
            self.button_frame.pack_forget()
        else:
            self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)"""

    def show_buttons_keybind(self, event=None):
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def hide_buttons_keybind(self, event=None):
        self.button_frame.pack_forget()

    def mute_audio_keybind(self, event=None):
        self.player.audio_toggle_mute()

    def unfullscreen_keybind(self, event=None):
        self.player.set_fullscreen(False)
        self.root.attributes("-fullscreen", False)

    def skip_time_keybind(self, event=None):
        current_time = self.player.get_time()

        if event.keysym == "Left":
            new_time = current_time - 5 * 1000
            self.player.set_time(max(new_time, 0))
        elif event.keysym == "Right":
            new_time = current_time + 5 * 1000
            self.player.set_time(new_time)

    def volume_keybind(self, event=None):
        curr_volume = self.player.audio_get_volume()
        print(curr_volume)
        if event.keysym == "Up":
            new_volume = curr_volume + 10
            if new_volume > 100:
                new_volume = 100
            self.player.audio_set_volume(new_volume)
        elif event.keysym == "Down":
            new_volume = curr_volume - 10
            if new_volume < 0:
                new_volume = 0
            self.player.audio_set_volume(new_volume)

    def slider_volume(self):
        return