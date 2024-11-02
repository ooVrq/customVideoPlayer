import tkinter as tk
from tkinter import messagebox
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
        self.root.configure(bg="black")

        self.root.iconbitmap("icons/icon.ico")

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

        # Set current path to nothing to ensure :s working
        self.curr_path = ""

        # Set current audio and sub track to defaults
        self.curr_audio_track = 1
        self.curr_sub_track = -1

        # Handle turning on/off keybinds.txt for console input
        self.load_keybinds()
        self.enable_keybinds()
        self.console_input.bind("<FocusIn>", self.disable_keybinds)
        self.console_input.bind("<FocusOut>", self.enable_keybinds)

    def load_keybinds(self):
        self.keybinds = {}
        with open("keybinds.txt", "r") as file:
            for line in file:
                if "=" in line:
                    key, function_name = line.strip().split("=")
                    key = key.strip()
                    function_name = function_name.strip()
                    self.keybinds[function_name] = key

        print(self.keybinds)


    # Enable and disabling every keybind
    def enable_keybinds(self, event=None):
        for function_name, key in self.keybinds.items():
            function = getattr(self, function_name, None)
            if function:
                self.root.bind(f"<KeyPress-{key}>", function)

        self.root.bind(f"<KeyRelease-{self.keybinds.get("show_buttons_keybind")}>", self.hide_buttons_keybind)
        self.root.bind("<KeyPress-Escape>", self.unfullscreen_keybind)
        self.root.bind("<KeyPress-Left>", self.skip_time_keybind)
        self.root.bind("<KeyPress-Right>", self.skip_time_keybind)
        self.root.bind("<KeyPress-Up>", self.volume_keybind)
        self.root.bind("<KeyPress-Down>", self.volume_keybind)
        self.console_input.unbind("<Return>")

    def disable_keybinds(self, event=None):
        for function, key in self.keybinds.items():
            self.root.unbind(f"<KeyPress-{key}>")
        self.root.unbind(f"<KeyRelease-{self.keybinds.get("show_buttons_keybind")}>")
        self.root.unbind("<KeyPress-Escape>")
        self.root.unbind("<KeyPress-Left>")
        self.root.unbind("<KeyPress-Right>")
        self.root.unbind("<KeyPress-Up>")
        self.root.unbind("<KeyPress-Down>")
        self.console_input.bind("<Return>", self.check_input)

    # When the video player is closed
    def window_closed(self):
        self.save_progress()
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
        # self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_frame = tk.Frame(self.button_frame, bg=self.button_color)
        self.bottom_frame.grid(row=1, column=0, sticky="ew", columnspan=3, padx=10, pady=5)

        # Pause Button
        self.play_image = Image.open("icons/isplay.png")
        self.play_image = self.play_image.resize((25, 25))
        self.play_photo = ImageTk.PhotoImage(self.play_image)
        self.pause_image = Image.open("icons/ispause.png")
        self.pause_image = self.pause_image.resize((25, 25))
        self.pause_photo = ImageTk.PhotoImage(self.pause_image)
        self.pause_button = tk.Button(self.bottom_frame, image=self.play_photo, command=self.pause_video,)

        # Fullscreen Button
        self.fullscreen_image = Image.open("icons/fullscreen.png")
        self.fullscreen_image = self.fullscreen_image.resize((20, 20))
        self.fullscreen_photo = ImageTk.PhotoImage(self.fullscreen_image)
        self.toggle_fullscreen = tk.Button(self.bottom_frame, image=self.fullscreen_photo, command=self.set_fullscreen)

        # Volume Slider
        self.volume_label = tk.Label(self.bottom_frame, text="0%", width=4, bg=self.button_color)
        self.volume_slider = ttk.Scale(self.bottom_frame, from_=0, to=100, orient=tk.HORIZONTAL,  command=self.slider_volume)
        self.volume_label.pack(side=tk.RIGHT, padx=0)
        self.volume_slider.pack(side=tk.RIGHT, padx=5)

        # Prev Button
        self.prev_image = Image.open("icons/previous.png")
        self.prev_image = self.prev_image.resize((20, 20))
        self.prev_photo = ImageTk.PhotoImage(self.prev_image)
        self.prev_button = tk.Button(self.bottom_frame, image=self.prev_photo, command=self.previous_video)

        # Stop Button
        self.stop_image = Image.open("icons/stop.png")
        self.stop_image = self.stop_image.resize((20, 20))
        self.stop_photo = ImageTk.PhotoImage(self.stop_image)
        self.stop_button = tk.Button(self.bottom_frame, image=self.stop_photo, command=self.stop_video)

        # Next Button
        self.next_image = Image.open("icons/next.png")
        self.next_image = self.next_image.resize((20, 20))
        self.next_photo = ImageTk.PhotoImage(self.next_image)
        self.next_button = tk.Button(self.bottom_frame, image=self.next_photo, command=self.next_video)

        # Pack all buttons
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.prev_button.pack(side=tk.LEFT, padx=(20, 5))
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.LEFT, padx=(5, 0))
        self.toggle_fullscreen.pack(side=tk.LEFT, padx=(20, 5))

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
        if input == "s" or input == "save":
            self.save_progress()
        if input == "pause":
            self.player.pause()
        if input == "play":
            self.player.play()
        if bool(re.fullmatch(r"\d{4}|\d{2}:\d{2}|\d{3}|\d{2}|\d{1}|\d{1}:\d{2}:\d{2}", input)):
            self.set_video_time(input)
        if input == "setfile" or input == "sf" or input == "next":
            self.save_progress()
            self.play_video(input)
        if input == "playlist":
            self.open_from_save()
        if input == "cyclesub":
            self.cycle_subtitle()
        if input == "cycleaudio":
            self.cycle_audio()

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
        elif bool(re.fullmatch(r"\d{4}", time)):
            min = time[:2]
            sec = time[2:]

        elif bool(re.fullmatch(r"\d{3}", time)):
            min = time[0]
            sec = time[1:]
        elif bool(re.fullmatch(r"\d{2}|\d{1}", time)):
            min = time

        elif bool(re.fullmatch(r"\d{1}:\d{2}:\d{2}", time)):
            hour, min, sec = time.split(":")

        # Valid second input check
        if int(sec) > 59:
            return

        # Time to ms
        time_ms = (int(hour) * 3600 + int(min) * 60 + int(sec)) * 1000
        self.player.set_time(time_ms)

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
            self.root.title("oVideo - Playing: " + os.path.basename(self.curr_path)[:-4])
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
        self.root.title("oVideo - Playing: " + os.path.basename(self.curr_path)[:-4])

    def play_prev_file(self):
        self.curr_path = self.get_prev_file()

        if self.player.is_playing():
            self.player.stop()

        new_media_obj = self.vlc_instance.media_new(self.curr_path)

        self.player.set_media(new_media_obj)
        self.player.play()
        self.root.title("oVideo - Playing: " + os.path.basename(self.curr_path)[:-4])

    def get_prev_file(self):
        file_path = self.curr_path
        file_directory = os.path.dirname(file_path)
        files = sorted(os.listdir(file_directory))

        raw_file_name = os.path.basename(file_path)

        # Use a try to catch last file in folder error
        try:
            curr_index = files.index(raw_file_name)
            return os.path.join(file_directory, files[curr_index - 1])
        except IndexError:
            print("Last file in Folder")

    # Creation of progress bar
    def create_progress_bar(self):
        # Create and pack progress bar frame
        self.progress_frame = tk.Frame(self.button_frame, bg=self.button_color, height=30)
        # self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 2))

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
        self.progress_bar = tk.Canvas(self.progress_frame, bg="lightgray", height=15)
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

    # Handles time skipping related keybinds.txt
    def skip_time_keybind(self, event=None):
        current_time = self.player.get_time()

        if event.keysym == "Left":
            new_time = current_time - 5 * 1000
            self.player.set_time(max(new_time, 0))
        elif event.keysym == "Right":
            new_time = current_time + 5 * 1000
            self.player.set_time(new_time)

    # Handles volume keybinds.txt
    def volume_keybind(self, event=None):
        curr_volume = self.player.audio_get_volume()
        if event.keysym == "Up":
            new_volume = curr_volume + 5
            if new_volume > 100:
                new_volume = 100
            self.player.audio_set_volume(new_volume)
            self.update_volume_bar(new_volume)
        elif event.keysym == "Down":
            new_volume = curr_volume - 5
            if new_volume < 0:
                new_volume = 0
            self.player.audio_set_volume(new_volume)
            self.update_volume_bar(new_volume)

    # Still unimplemented - Handles functionality of volume slider in button menu
    def slider_volume(self, event=None):
        volume = int(self.volume_slider.get())
        self.volume_label.config(text=str(volume)+"%")
        self.player.audio_set_volume(volume)

    def update_volume_bar(self, volume):
        self.volume_label.config(text=str(volume)+"%")
        self.volume_slider.set(volume)

    def previous_video(self, event=None):
        self.play_prev_file()

    def next_video(self, event=None):
        self.play_next_file()

    def stop_video(self, event=None):
        self.player.stop()
        self.curr_path = ""

    def anime_skip(self, event=None):
        current_time = self.player.get_time()
        new_time = current_time + 89 * 1000
        self.player.set_time(max(new_time, 0))

    # Handles all saving progress of videos
    def save_progress(self):
        # Get the video object from player
        current_file = self.curr_path

        # Check if video is actually being played before starting save
        if current_file != "":
            file_name = os.path.basename(current_file)
            dir_name = os.path.dirname(current_file)

            files_in_dir = sorted(os.listdir(dir_name))

            current_time = self.player.get_time()

            with open("saveData.txt", "r") as data:
                data_list = data.readlines()

            found_dir = False
            replace_data = False

            for i in range(len(data_list)):
                if data_list[i].lstrip("d").rstrip("\n") == dir_name:
                    found_dir = True
                    old_path = data_list[i + 1].lstrip("f").rstrip("\n")
                    old_time = int(data_list[i + 2].lstrip("t").rstrip("\n"))

                    old_index = files_in_dir.index(old_path)
                    new_index = files_in_dir.index(file_name)

                    if new_index > old_index:
                        data_list[i + 1] = "f" + file_name + "\n"
                        data_list[i + 2] = "t" + str(current_time) + "\n"
                        replace_data = True
                        break
                    elif new_index == old_index:
                        if current_time > old_time:
                            data_list[i + 1] = "f" + file_name + "\n"
                            data_list[i + 2] = "t" + str(current_time) + "\n"
                            replace_data = True
                            break

            # Adds new directory entry as the current save
            if not found_dir:
                data_list.append("d" + dir_name + "\n")
                data_list.append("f" + file_name + "\n")
                data_list.append("t" + str(current_time) + "\n")
            with open("saveData.txt", "w") as data:
                data.writelines(data_list)

    # Handles opening from a save file
    def open_from_save(self, event=None):
        dir_path = filedialog.askdirectory(title="Select a Folder")

        with open("saveData.txt", "r") as data:
            data_list = data.readlines()

        full_path = ""
        time = 0
        save_found = False

        for i in range(len(data_list)):
            if data_list[i].startswith("d"):
                raw_dir = data_list[i].lstrip("d").rstrip("\n")

                if raw_dir == dir_path:
                    file_name = data_list[i + 1].lstrip("f").rstrip("\n")
                    time = int(data_list[i + 2].lstrip("t").rstrip("\n"))
                    full_path = os.path.join(dir_path, file_name)
                    save_found = True
                    break

        if save_found:
            file = self.vlc_instance.media_new(full_path)

            if self.player.is_playing():
                self.player.stop()

            self.player.set_media(file)
            self.player.play()
            self.player.set_time(time)
            self.curr_path = full_path
            self.root.title("oVideo - Playing: " + file_name[:-4])


        else:
            messagebox.showinfo("Error", "Save data not found")

    def cycle_subtitle(self, event=None):
        subtitle_tracks = self.player.video_get_spu_description()
        if len(subtitle_tracks) > 0:
            self.curr_sub_track = (self.curr_sub_track + 1) % len(subtitle_tracks)
            self.player.video_set_spu(subtitle_tracks[self.curr_sub_track][0])


    def cycle_audio(self, event=None):
        audio_tracks = self.player.audio_get_track_description()
        print(self.player.audio_get_track_description())
        if len(audio_tracks) > 0:
            self.curr_audio_track = (self.curr_audio_track + 1) % len(audio_tracks)
            self.player.audio_set_track(audio_tracks[self.curr_audio_track][0])