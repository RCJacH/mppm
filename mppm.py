import tkinter as tk
from music_production_project_manager.gui.gui_audio_file import FolderBrowser

if __name__ == "__main__":
    root = tk.Tk()
    cls = FolderBrowser(root)
    root.mainloop()
