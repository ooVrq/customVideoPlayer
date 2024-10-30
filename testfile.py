import os
import vlc
import tkinter as tk
from tkinter import filedialog

class MyGUI:
    def __init__(self):
        self.main_window = tk.Tk()

        self.main_window.geometry("700x450")
        self.main_window.config(bg="black")

        self.button = tk.Button(text="Enter Repository Folder", command=self.button_press)
        self.button.pack()
        self.main_window.mainloop()

        self.menubar = tk.Menu(self.main_window)

        self.change_repository = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label = 'Testing', menu = self.change_repository)
        self.change_repository.add_command(label = "test1", command = None)
        self.main_window.config(menu=self.menubar)
    # Gets a file and sends the path to get_next_file and then displays and plays the file
    """def button_press(self, event=None):
        file_path = filedialog.askopenfilename()
        next_file_path = self.get_next_file(file_path)
        print(next_file_path)
        # self.play_next_file(next_file_path)"""

    def button_press(self, event=None):
        user_data = open("userData.txt", "r")
        dir_in_file = user_data.readline().strip()
        print(dir_in_file)
        if dir_in_file == "":
            repository_path = filedialog.askdirectory()
            write_user_data = open("userData.txt", "w")
            write_user_data.write(repository_path)
        else:
            repository_path = dir_in_file
        main_files = sorted(os.listdir(repository_path))
        for i in range(len(main_files)):
            file = main_files[i]
            if not file.startswith("."):
                file_path = os.path.join(repository_path, file)
                if os.path.isfile(file_path):
                    print(file)
                else:
                    print(file)

    def get_next_file(self, file_path):
        file_directory = os.path.dirname(file_path)
        files = sorted(os.listdir(file_directory))

        raw_file_name = os.path.basename(file_path)

        # Use a try to catch last file in folder error
        try:
            curr_index = files.index(raw_file_name)
            return os.path.join(file_directory, files[curr_index + 1])
        except IndexError:
            print("Last file in Folder")

    def play_next_file(self, path):
        if self.player.is_playing():
            self.player.stop()

        new_media_obj = self.instance.media_new(path)

        self.player.set_media(new_media_obj)
        self.player.play()

def main():

    new_window = MyGUI()
main()