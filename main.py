import tkinter as tk
from mppm.gui import FolderBrowser

if __name__ == "__main__":
    root = tk.Tk()
    cls = FolderBrowser(root)
    root.mainloop()
