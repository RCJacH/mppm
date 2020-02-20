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
        self.display_file_list()

    def display_header(self):
        def browse_button():
            path = tk.filedialog.askdirectory()
            if path:
                self.path = path
                self.address.delete(0, tk.END)
                self.address.insert(0, path)

        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.header_left = ttk.Frame(self.header_frame)
        self.header_left.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.title = ttk.Label(self.header_left, text="Title")
        self.title.pack(side=tk.TOP, anchor=tk.W)
        self.address = ttk.Entry(self.header_left)
        self.address.pack(side=tk.LEFT)
        self.browse = ttk.Button(self.header_left, text="Browse", command=browse_button)
        self.browse.pack(side=tk.LEFT)
        self.header_mid = ttk.Frame(self.header_frame)
        self.header_mid.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.header_right = ttk.Frame(self.header_frame)
        self.header_right.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.analyze = ttk.Button(self.header_right, text="Analyze")
        self.analyze.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def display_file_list(self):
        self.file_list_frame = ttk.Frame(self)
        self.file_list_frame.pack(side=tk.TOP)
        self.scrollbar = ttk.Scrollbar(self.file_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_list = tk.Listbox(
            self.file_list_frame,
            width=16,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
        )
        self.action_list.pack(side=tk.LEFT, fill=tk.Y)
        self.channels_list = tk.Listbox(
            self.file_list_frame,
            width=8,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
        )
        self.channels_list.pack(side=tk.LEFT, fill=tk.Y)
        self.property_list = tk.Listbox(
            self.file_list_frame,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
        )
        self.property_list.pack(side=tk.LEFT, fill=tk.Y)
        self.file_list = tk.Listbox(
            self.file_list_frame,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
        )
        self.file_list.pack(side=tk.RIGHT, fill=tk.Y)
        for i in range(1):
            self.file_list.insert(tk.END, "")
            self.property_list.insert(tk.END, "")
            self.channels_list.insert(tk.END, "")
            self.action_list.insert(tk.END, "")

        self.scrollbar.config(command=self.file_list.yview)
        pass

    def display_actions(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    cls = FolderBrowser(root)
    root.mainloop()
