import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from music_production_project_manager.folder_handler import FileList

class FolderBrowser(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._FileList = FileList()
        self.master = master
        self.pack()
        self.path = ""
        self.display_header()
        self.display_file_list()

    def display_header(self):
        def browse_button(address):
            path = tk.filedialog.askdirectory()
            if path:
                self.path = path
                address.delete(0, tk.END)
                address.insert(0, path)

        def analyze_button():
            self._FileList.search_folder(self.path)

        frame = ttk.Frame(self)
        left = ttk.Frame(frame)
        mid = ttk.Frame(frame)
        right = ttk.Frame(frame)

        title = ttk.Label(left, text="Title")
        title.pack(side=tk.TOP, anchor=tk.W)
        address = ttk.Entry(left, width=36)
        address.pack(side=tk.LEFT)
        browse = ttk.Button(left, text="Browse", command=lambda: browse_button(address))
        browse.pack(side=tk.LEFT)

        analyze = ttk.Button(right, text="Analyze", command=analyze_button)
        analyze.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        left.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        right.pack(side=tk.RIGHT, expand=False, fill=tk.Y)
        mid.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        frame = frame
        frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def display_file_list(self):
        frame = ttk.Frame(self)
        tree = ttk.Treeview(frame, columns=("Channels", "Identical", "Action"))
        scroll = ttk.Scrollbar(frame, command=tree.yview)
        tree.configure(yscroll=scroll)
        tree.heading("#0", text="Filename")
        tree.column("#0", width=384, stretch=False)
        tree.heading("#1", text="Channels")
        tree.column("#1", width=64, stretch=False, anchor=tk.N)
        tree.heading("#2", text="Identical")
        tree.column("#2", width=64, stretch=False, anchor=tk.N)
        tree.heading("Action", text="Action")
        tree.column("Action", width=128, stretch=False, anchor=tk.N)
        for filename in self._FileList.filenames:
            tree.insert('', "end", text=filename)

        self.file_list_frame = frame
        self.file_list_frame.pack(side=tk.TOP)
        self.file_tree = tree
        tree.pack(side=tk.LEFT, fill=tk.Y)
        scroll.pack(side=tk.LEFT, fill=tk.Y)

    def display_actions(self):
        pass
