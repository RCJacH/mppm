import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from music_production_project_manager.folder_handler import FileList

import logging

logger = logging.getLogger(__name__)


class FolderBrowser(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        logger.debug("Initializing %s", self.__class__.__name__)
        super().__init__(master, *args, **kwargs)
        self._FileList = FileList()
        self.master = master
        self.pack()
        self.path = ""
        self.display_header()
        self.display_file_list()
        self.display_actions()
        logger.debug("Initializing %s", self.__class__.__name__)

    def display_header(self):
        def browse_button(address):
            path = tk.filedialog.askdirectory()
            if path:
                self.path = path
                address.delete(0, tk.END)
                address.insert(0, path)

        def analyze_button():
            def check(v):
                return "x" if v else ""

            def select(v):
                return v

            self._FileList.search_folder(self.path)
            self.file_tree.delete(*self.file_tree.get_children())
            for file in self._FileList.files:
                self.file_tree.insert(
                    "",
                    "end",
                    text=file.filename,
                    values=[
                        file.channels,
                        check(file.isEmpty),
                        check(file.isMono),
                        check(file.isFakeStereo),
                        check(file.isStereo),
                        check(file.isMultichannel),
                        select(file.action),
                    ],
                )

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
        frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def display_file_list(self):
        x_width = 40
        frame = ttk.Frame(self)
        tree = ttk.Treeview(
            frame,
            columns=("Channels", "Empty", "Mono", "Fake", "Stereo", "Multi", "Action"),
        )
        scroll = ttk.Scrollbar(frame, command=tree.yview)
        tree.configure(yscroll=scroll)
        tree.heading("#0", text="Filename")
        tree.column("#0", width=128, stretch=False)
        tree.heading("#1", text="Channels")
        tree.column("#1", width=64, stretch=False, anchor=tk.N)
        tree.heading("Empty", text="Empty")
        tree.column("Empty", width=x_width, stretch=False, anchor=tk.N)
        tree.heading("Mono", text="Mono")
        tree.column("Mono", width=x_width, stretch=False, anchor=tk.N)
        tree.heading("Fake", text="Fake")
        tree.column("Fake", width=x_width, stretch=False, anchor=tk.N)
        tree.heading("Stereo", text="Stereo")
        tree.column("Stereo", width=x_width, stretch=False, anchor=tk.N)
        tree.heading("Multi", text="Multi")
        tree.column("Multi", width=x_width, stretch=False, anchor=tk.N)
        tree.heading("Action", text="Action")
        tree.column("Action", width=128, stretch=False, anchor=tk.N)

        self.file_list_frame = frame
        self.file_list_frame.pack(side=tk.TOP)
        self.file_tree = tree
        tree.pack(side=tk.LEFT, fill=tk.Y)
        scroll.pack(side=tk.LEFT, fill=tk.Y)

    def display_actions(self):
        def proceed_button():
            for file in self._FileList.files:
                file.proceed()

        frame = ttk.Frame(self)
        proceed = ttk.Button(frame, text="Proceed", command=proceed_button)
        proceed.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)