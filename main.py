import vlc
from menus import VLCApp
import tkinter as tk
from PIL import Image, ImageTk

def main():
    my_page = VLCApp()
    my_page.play_video()


    tk.mainloop()

    input()
    print("test")
main()

