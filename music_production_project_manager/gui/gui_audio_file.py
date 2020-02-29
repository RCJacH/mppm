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
        self.noBackup = tk.BooleanVar()
        self.skipMonoize = tk.BooleanVar()
        self.skipRemove = tk.BooleanVar()
        self.display_header()
        self.display_file_list()
        self.display_actions()
        logger.debug("Initializing %s", self.__class__.__name__)

    def display_header(self):
        def browse_button(address):
            path = tk.filedialog.askdirectory(initialdir=self.path)
            if path:
                self.path = path
                address.delete(0, tk.END)
                address.insert(0, path)

        def analyze_command(v):
            def check(v):
                return "x" if v else ""

            def select(v):
                return v

            options = {"threshold": float(v.get())}
            self._FileList.update_options(options)
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
        top = ttk.Frame(frame)
        left = ttk.Frame(frame)
        mid = ttk.Frame(frame)
        right = ttk.Frame(frame)

        title = ttk.Label(top, text="Music Production Project Manager")
        title.pack(side=tk.TOP, anchor=tk.W)
        address_label = ttk.Label(left, text="Select Folder:")
        address_label.pack(side=tk.TOP, anchor=tk.W)
        address = ttk.Entry(left, width=36)
        address.pack(side=tk.LEFT)
        browse = ttk.Button(left, text="Browse", command=lambda: browse_button(address))
        browse.pack(side=tk.LEFT)

        sep = ttk.Separator(left, orient="vertical")
        sep.pack(side=tk.LEFT)

        threshold_label = ttk.Label(mid, text="Null threshold")
        threshold_label.pack(side=tk.TOP, anchor=tk.W)
        threshold = ttk.Entry(mid, width=12)
        threshold.insert(0, "{:.20f}".format(self._FileList.options["threshold"]).rstrip('0'))
        threshold.pack(side=tk.LEFT)
        analyze = ttk.Button(right, text="Analyze", command=lambda: analyze_command(threshold))
        analyze.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        top.pack(side=tk.TOP, expand=False, fill=tk.Y)
        left.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        right.pack(side=tk.RIGHT, expand=False, fill=tk.Y)
        mid.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def display_file_list(self):
        x_width = 42
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
        def proceed_command():
            options = {
                "noBackup": self.noBackup,
                "skipMonoize": self.skipMonoize,
                "skipRemove": self.skipRemove
            }
            self._FileList.update_options(options)
            self._FileList.proceed()

        def backup_command(v):
            self.noBackup = v

        def skipMonoize_command(v):
            self.skipMonoize = v

        def skipRemove_command(v):
            self.skipRemove = v

        frame = ttk.Frame(self)
        top = tk.Frame(frame)
        bottom = tk.Frame(frame)
        proceed = ttk.Button(bottom, text="Proceed", command=proceed_command)
        proceed.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        backup = tk.Checkbutton(
            top,
            text="Back up to sub-folder: ",
            variable=self.noBackup,
            onvalue=False,
            offvalue=True,
            height=5,
            width=20,
            command=lambda: backup_command(self.noBackup.get()),
        )
        skipMonoize_button = tk.Checkbutton(
            top,
            text="Skip Monoize",
            variable=self.skipMonoize,
            height=5,
            width=20,
            command=lambda: skipMonoize_command(self.skipMonoize.get()),
        )
        skipRemove_button = tk.Checkbutton(
            top,
            text="Skip Monoize",
            variable=self.skipRemove,
            height=5,
            width=20,
            command=lambda: skipRemove_command(self.skipRemove.get()),
        )
        address = ttk.Entry(top, width=16)
        address.insert(0, self._FileList.options["backup"]["folder"])

        backup.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
        address.pack(side=tk.LEFT, expand=True, fill=tk.X)
        skipMonoize_button.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
        skipRemove_button.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
        top.pack(side=tk.TOP, expand=False, fill=tk.X)
        bottom.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
