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

        # Initial size of video player
        x = 1000
        self.root.geometry(f"{x}x{int(x * 9/16)}")

        # Frame for the video creation
        self.create_video()

        # Frame overlay for the buttons
        self.create_button_overlay()

        # Create VLC instance named vlc_instance
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.set_output()

        self.create_console()

        # Create and start updating progress bar
        self.create_progress_bar()
        self.update_progress_bar()

        # Update progress bar on resize
        self.root.bind("<Configure>", self.on_resize)

        # On window close
        self.root.protocol("WM_DELETE_WINDOW", self.window_closed)

        # Variable for checking update time for bar slider throttling to reduce lag
        self.last_update_time = 0

        # Handle turning on/off keybinds for console input
        self.enable_keybinds()
        self.console_input.bind("<FocusIn>", self.disable_keybinds)
        self.console_input.bind("<FocusOut>", self.enable_keybinds)

    # Enable and disabling every keybind
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

    # When the video player is closed
    def window_closed(self):
        self.player.stop()
        self.player.release()
        self.root.destroy()
        sys.exit()

    # Handles creation of entire button frame
    def create_button_overlay(self):
        # Button Frame initialization
        self.button_color = "MediumPurple3"
        self.button_frame = tk.Frame(self.root, bg=self.button_color)

        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Start program by packing or unpacking button frame
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.top_frame = tk.Frame(self.button_frame, bg=self.button_color)
        self.top_frame.grid(row=0, column=0, sticky="ew", columnspan=3, padx=10, pady=5)

        # Pause Button
        self.play_image = Image.open("icons/isplay.png")
        self.play_photo = ImageTk.PhotoImage(self.play_image)
        self.pause_image = Image.open("icons/ispause.png")
        self.pause_photo = ImageTk.PhotoImage(self.pause_image)
        self.pause_button = tk.Button(self.top_frame, image=self.play_photo, command=self.pause_video,)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Fullscreen Button
        self.fullscreen_image = Image.open("icons/fullscreen.png")
        self.fullscreen_photo = ImageTk.PhotoImage(self.fullscreen_image)
        self.toggle_fullscreen = tk.Button(self.top_frame, image=self.fullscreen_photo, command=self.set_fullscreen)
        self.toggle_fullscreen.pack(side=tk.LEFT, padx=5)

        # Volume Slider
        self.volume_label = tk.Label(self.top_frame, text="Volume: 0%", width=10)
        self.volume_slider = ttk.Scale(self.top_frame, from_=0, to=100, orient=tk.HORIZONTAL,  command=self.slider_volume)
        self.volume_label.pack(side=tk.RIGHT, padx=5)
        self.volume_slider.pack(side=tk.RIGHT, padx=5)

    def create_console(self):
        font_style = tkFont.Font(family="Courier New", size=12, weight="normal")
        self.console_color = "navy"

        # Console frame creation
        self.console_frame = tk.Frame(self.root, bg=self.console_color)

        # Decorative colon in front of console
        self.colon_label = tk.Label(self.console_frame, font=font_style, bg=self.console_color, fg="white", text=":")
        self.colon_label.pack(side=tk.LEFT)

        # Entry for console
        self.console_input = tk.Entry(self.console_frame, bg=self.console_color, font=font_style, fg="white")
        self.console_input.pack(side=tk.LEFT, padx=(0, 10))

    # Packs console frame, sets focus in the input, and deletes previous input when : is pressed
    def show_console(self, event=None):
        self.console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.console_input.focus_set()
        self.console_input.delete(0, tk.END)

    # Called on enter key. Handles all commands sent through console
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

        # Hides console frame and sets focus back on root after checking command
        self.console_frame.pack_forget()
        self.root.focus_set()

    # Called when a set time console command is run
    def set_video_time(self, time):

        hour = min = sec = 0

        # XX:XX case
        if bool(re.fullmatch(r"\d{2}:\d{2}", time)):
            min, sec = time.split(":")

        # XXXX case
        elif bool(re.fullmatch(r"\d{4}|\d{3}", time)):
            min = time[:2]
            # test making changes
            sec = time[2:]

        elif bool(re.fullmatch(r"\d{2}|\d{1}", time)):
            min = time

        elif bool(re.fullmatch(r"\d{1}:\d{2}:\d{2}", time)):
            hour, min, sec = time.split(":")

        # Valid second input check
        if int(sec) > 59 or int(min) > 59:
            return

        # Time to ms
        time_ms = (int(hour) * 3600 + int(min) * 60 + int(sec)) * 1000
        self.player.set_time(time_ms)

        print(min, sec)

    # Initial creation of canvas where video is played
    def create_video(self):
        self.video_frame = tk.Canvas(self.root, bg="purple")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

    # Sets output (currently only windows supported)
    def set_output(self):
        self.player.set_hwnd(self.video_frame.winfo_id())

    # Handles :sf and :next commands
    def play_video(self, input):
        if self.player.is_playing():
            self.player.stop()

        if input == "sf" or input == "setfile":
            self.get_new_file()
            file = self.vlc_instance.media_new(self.curr_path)

            self.player.set_media(file)
            self.player.play()
        elif input == "next":
            self.play_next_file()

        self.volume_slider.set(self.player.audio_get_volume())

    # Called through the play_video method to prompt file input from user. Sets curr_path
    # to file user selects
    def get_new_file(self):
        file_types = [("Video Files", "*.mp4;*.mkv;*.avi;*.mov"), ("Audio Files", "*.mp3;*.wav"),
                      ("All Files", "*.*")]
        self.curr_path = filedialog.askopenfilename(filetypes=file_types)

    # Is called from the play_next_file method. Returns the next file in the folder that
    # the current file is being played on
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

    # Called from :next console input. Gets next file in folder and plays it
    def play_next_file(self):
        self.curr_path = self.get_next_file()

        if self.player.is_playing():
            self.player.stop()

        new_media_obj = self.vlc_instance.media_new(self.curr_path)

        self.player.set_media(new_media_obj)
        self.player.play()

    # Creation of progress bar
    def create_progress_bar(self):
        # Create and pack progress bar frame
        self.progress_frame = tk.Frame(self.button_frame, bg=self.button_color, height=30)
        # self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        self.progress_frame.grid_columnconfigure(1, weight=1)

        # Create and pack current runtime of video playing to the left of bar
        self.curr_time = tk.Label(self.progress_frame, text="00:00", bg=self.button_color)
        # self.curr_time.pack(side=tk.LEFT, padx=(0, 5))
        self.curr_time.grid(row=0, column=0, padx=(0, 5))

        # Create and pack total runtime of video playing to the right of bar
        self.total_time = tk.Label(self.progress_frame, text="00:00", bg=self.button_color)
        # self.total_time.pack(side=tk.RIGHT, padx=(5, 0))
        self.total_time.grid(row=0, column=2, padx=(5, 0))

        # Creation of progress bar
        self.progress_bar = tk.Canvas(self.progress_frame, bg="lightgray", height=20)
        # self.progress_bar.pack(fill=tk.BOTH, expand=True)
        self.progress_bar.grid(row=0, column=1, sticky="ew")

        self.bg_color = "lightgray"
        self.progress_bg = self.progress_bar.create_rectangle(0, 0, 0, 20, fill=self.bg_color, outline="")

        self.fg_color = "blue"
        self.progress_fg = self.progress_bar.create_rectangle(0, 0, 0, 20, fill=self.fg_color, outline="")

        # Gets inputs related to progress bar
        self.progress_bar.bind("<Button-1>", self.set_bar_time)
        self.progress_bar.bind("<B1-Motion>", self.drag_time)

    # Called from init and runs
    def update_progress_bar(self):
        # Get video info
        current_time = self.player.get_time()
        total_time = self.player.get_length()

        # Get dimensions
        canvas_width = self.progress_bar.winfo_width()

        # Update bar
        if total_time > 0:
            percent_complete = (current_time / total_time) * canvas_width
            self.progress_bar.coords(self.progress_fg, 0, 0, percent_complete, 20)
            self.curr_time.config(text=self.format_time(current_time))
            self.total_time.config(text=self.format_time(total_time))
        else:
            self.progress_bar.coords(self.progress_fg, 0, 0, 0, 20)

        # Calls itself after 1 second
        self.root.after(1000, self.update_progress_bar)

    # Called in update_progress_bar to update the current time of the video. Converts raw time to
    # formatted time
    def format_time(self, time):
        total_seconds = time // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # Updates bar when resized
    def on_resize(self, event):
        self.update_progress_bar()

    # Called when bar is clicked on and updates bar and time accordingly
    def set_bar_time(self, event):
        bar_length = self.progress_bar.winfo_width()
        click_x = event.x
        total_time = self.player.get_length()

        if total_time > 0:
            percent = click_x / bar_length
            new_time = int(percent * total_time)
            self.progress_bar.coords(self.progress_fg, 0, 0, click_x, 20)
            self.player.set_time(new_time)

    # Called when bar is dragged. Updates bar and time accordingly
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

    # Called when pause button or pause keybind is pressed
    def pause_video(self, event=None):
        if self.player.is_playing():
            self.pause_button.config(image=self.pause_photo)
            self.player.pause()
        else:
            self.pause_button.config(image=self.play_photo)
            self.player.pause()

    # Called when fullscreen button or keybind is pressed
    def set_fullscreen(self, event=None):
        fullscreen_state = self.player.get_fullscreen()
        print(fullscreen_state)
        self.player.set_fullscreen(not fullscreen_state)
        self.root.attributes("-fullscreen", not fullscreen_state)

    # Toggles the button menu on/off
    """def toggle_buttons_keybind(self, event=None):
        if self.button_frame.winfo_ismapped():
            self.button_frame.pack_forget()
        else:
            self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)"""

    # Shows buttons when key is held
    def show_buttons_keybind(self, event=None):
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Hides buttons when key is released
    def hide_buttons_keybind(self, event=None):
        self.button_frame.pack_forget()

    # Mutes audio when button or keybind is pressed
    def mute_audio_keybind(self, event=None):
        self.player.audio_toggle_mute()

    # Specifically unfullscreens when unfullscreen keybind is pressed
    def unfullscreen_keybind(self, event=None):
        self.player.set_fullscreen(False)
        self.root.attributes("-fullscreen", False)

    # Handles time skipping related keybinds
    def skip_time_keybind(self, event=None):
        current_time = self.player.get_time()

        if event.keysym == "Left":
            new_time = current_time - 5 * 1000
            self.player.set_time(max(new_time, 0))
        elif event.keysym == "Right":
            new_time = current_time + 5 * 1000
            self.player.set_time(new_time)

    # Handles volume keybinds
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

    # Still unimplemented - Handles functionality of volume slider in button menu
    def slider_volume(self, event=None):
        volume = int(self.volume_slider.get())
        self.volume_label.config(text="Volume: " + str(volume)+"%")
        self.player.audio_set_volume(volume)
        print(self.player.audio_get_volume())