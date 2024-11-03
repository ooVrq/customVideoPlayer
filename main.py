import vlc
from menus import VLCApp
import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD
import sys

def main():

    video_file = sys.argv[1] if len(sys.argv) > 1 else None
    root = TkinterDnD.Tk()

    my_page = VLCApp(root, video_file)

    tk.mainloop()

main()

