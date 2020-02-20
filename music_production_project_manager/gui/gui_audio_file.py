import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class FolderBrowser(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.pack()
        self.path = ""
        self.display_header()

    def display_header(self):
        def browse_button():
            path = tk.filedialog.askdirectory()
            if path:
                self.path = path
                self.address.delete(0, tk.END)
                self.address.insert(0, path)

        self.header_frame = ttk.Frame(self)
        self.title = ttk.Label(self.header_frame, text="Title")
        self.title.pack()
        self.address = ttk.Entry(self.header_frame)
        self.address.pack(side=tk.LEFT)
        self.browse = ttk.Button(self.header_frame, text="Browse", command=browse_button)
        self.browse.pack(side=tk.LEFT)
        self.analyze = ttk.Button(self.header_frame, text="Analyze")
        self.analyze.pack(side=tk.LEFT)
        self.header_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)


if __name__ == "__main__":
    root = tk.Tk()
    cls = FolderBrowser(root)
    root.mainloop()