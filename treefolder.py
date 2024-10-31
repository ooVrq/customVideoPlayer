import os
from moviepy.editor import VideoFileClip
import tkinter as tk
from tkinter import ttk

class FileTree:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")

        self.customize_styles()

        # Creation of Treeview widget
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Columns
        self.tree["columns"] = ("Size",)
        self.tree.column("#0", width=250, minwidth=250)
        self.tree.column("Size", width=100, minwidth=100)

        # Headings
        self.tree.heading("#0", text="Folders and Files", anchor=tk.W)

        self.load_directory(os.path.expanduser(r"F:\Shows"))

    def customize_styles(self):
        style = ttk.Style()
        style.theme_use("clam")  # or other themes like "alt", "default"
        style.configure("Treeview",
                        font=("Helvetica", 12),
                        background="black",
                        foreground="blue",
                        rowheight=25,
                        fieldbackground="black")
        style.map("Treeview",
                  background=[("selected", "purple")],
                  foreground=[("selected", "white")])
        style.configure("TScrollbar", background="#555", troughcolor="#222", arrowcolor="white")

    def load_directory(self, path, parent=""):

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # Adds folder to treeview
                    folder_id = self.tree.insert(parent, "end", text=item, values=("Folder",))
                    # Load subdirectory
                    self.load_directory(item_path, folder_id)
                else:
                    # Add file to treeview
                    self.tree.insert(parent, "end", text=item, values=("File",))
        except PermissionError:
            pass


def main():
    root = tk.Tk()
    new_window = FileTree(root)
    root.mainloop()
main()
