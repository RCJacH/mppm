import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


from music_production_project_manager.folder_handler import FileList
from .style import Mineral
from .style import core
from .style import components
from .default_style import DefaultSetting

import logging

logger = logging.getLogger(__name__)


class FolderBrowser:
    def __init__(self, master=None, *args, **kwargs):
        # super().__init__(master, *args, **kwargs)
        self._FileList = FileList()
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True, fill="both")
        self.path = tk.StringVar()
        self.threshold = tk.DoubleVar()
        self.noBackup = tk.BooleanVar()
        self.skipMonoize = tk.BooleanVar()
        self.skipRemove = tk.BooleanVar()
        self.current_stage = tk.IntVar()
        master.title("Music Production Project Manager")
        self.setup_style(self.master)

        top = ttk.Frame(self.frame)
        self.setup_header(top)
        self.setup_folder_selection(top)
        self.setup_input(top)
        self.fr_header.pack(anchor="n", expand=True, fill="x")
        self.fr_folder_selection.pack(anchor="n", expand=False, fill="x", padx=16)
        self.fr_input.pack(anchor="n", expand=False, fill="x", padx=16)
        top.pack(anchor="n", fill="x", ipady=8)

        mid = ttk.Frame(self.frame)
        self.display_file_list(mid)
        self.fr_file_list.pack(anchor="n", expand=True, fill="both", pady=16, padx=16)
        mid.pack(anchor="n", expand=True, fill="both")

        bottom = ttk.Frame(self.frame)
        self.display_actions(bottom)
        self.fr_actions.pack(side="bottom", expand=False, fill="x", padx=16)
        bottom.pack(anchor="n", fill="x")

        self.stage()
        # elif self.current_stage.get() > 1:

    def setup_style(self, master):
        s = ttk.Style()
        mineral = Mineral()
        s.theme_create("Mineral", settings=DefaultSetting()())
        s.theme_use("Mineral")
        # print(s.layout("TButton"))
        # print(s.element_options("TButton.focus"))
        # print(s.element_options("TButton.padding"))
        # print(s.lookup("TButton.border", "background"))
        # print(s.lookup("TButton.focus", "focuscolor"))

    def stage(self, value=None):
        if value is not None:
            self.current_stage.set(value)
        stage = self.current_stage.get()
        if stage == 0:
            self.bt_browse.state(["!disabled"])
            self.bt_analyze.state(["disabled"])
            self.bt_proceed.state(["disabled"])
        elif stage == 1:
            self.bt_browse.state(["readonly"])
            self.bt_analyze.state(["!disabled"])
            self.bt_proceed.state(["disabled"])
        elif stage == 2:
            self.bt_browse.state(["readonly"])
            self.bt_analyze.state(["readonly"])
            self.bt_proceed.state(["!disabled"])
        elif stage == -1:
            self.bt_browse.state(["disabled"])
            self.bt_analyze.state(["disabled"])
            self.bt_proceed.state(["disabled"])

    def setup_header(self, master):
        frame = ttk.Frame(master)
        title = ttk.Label(frame, text="Project Audio Files", style="Header.TLabel")
        title.pack(expand=True, fill="x")
        self.fr_header = frame

    def setup_folder_selection(self, master):
        frame = ttk.Frame(master)
        address_label = ttk.Label(frame, text="Select Folder:", style="Panel.TLabel")
        address_label.pack(side="left", anchor="n")
        self.address = ttk.Entry(frame)
        self.address.pack(side="left", expand=True, fill="x", padx=8)
        self.bt_browse = ttk.Button(frame, text="Browse", command=self.browse_command)
        self.bt_browse.pack(side="left", expand=False)

        self.fr_folder_selection = frame

    def browse_command(self):
        path = tk.filedialog.askdirectory(initialdir=self.path.get())
        if path:
            self.path.set(path)
            self.address.delete(0, tk.END)
            self.address.insert(0, path)
            self.stage(1)

    def setup_input(self, master):
        frame = ttk.Frame(master)
        top = ttk.Frame(frame)
        bottom = ttk.Frame(frame)

        threshold = ttk.LabelFrame(
            top,
            text="Null threshold",
            labelanchor="n",
            borderwidth=1,
            padding=[8, 8, 8, 16],
            relief="sunken",
        )
        en_threshold = ttk.Entry(threshold, justify="center")
        en_threshold.insert(
            0, "{:.20f}".format(self._FileList.options["threshold"]).rstrip("0")
        )
        en_threshold.pack(side="bottom")

        self.bt_analyze = ttk.Button(
            bottom, text="Analyze", command=self.analyze_command
        )
        # print(analyze.widgetName)
        # print(analyze.state(["readonly"]))
        # print(analyze.state())
        self.bt_analyze.pack(side="left", expand=True, fill="x")
        threshold.pack(side="left", expand=True, fill="x")
        top.pack(expand=True, fill="x")
        # ttk.Label(frame, text="").pack(side="top")
        bottom.pack(expand=True, fill="x", pady=8)

        self.fr_input = frame

    def analyze_command(self):
        def check(v):
            return "x" if v else ""

        def select(v):
            return v

        if not os.path.exists(self.path.get()):
            return self.stage(0)

        self.stage(-1)
        options = {"threshold": self.threshold.get()}
        self._FileList.update_options(options)
        self._FileList.search_folder(self.path.get())
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

        self.stage(2)

    def display_file_list(self, master):
        x_width = 60
        frame = ttk.Frame(master)
        tree = ttk.Treeview(
            frame,
            selectmode="browse",
            columns=("Channels", "Empty", "Mono", "Fake", "Stereo", "Multi", "Action"),
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scroll, yscrollcommand=scroll.set)
        tree.heading("#0", text="Filename")
        tree.column("#0", width=256, stretch=True)
        tree.heading("#1", text="Channels")
        tree.column("#1", width=96, stretch=False)
        tree.heading("Empty", text="Empty")
        tree.column("Empty", width=x_width, stretch=False)
        tree.heading("Mono", text="Mono")
        tree.column("Mono", width=x_width, stretch=False)
        tree.heading("Fake", text="Fake")
        tree.column("Fake", width=x_width, stretch=False)
        tree.heading("Stereo", text="Stereo")
        tree.column("Stereo", width=x_width, stretch=False)
        tree.heading("Multi", text="Multi")
        tree.column("Multi", width=x_width, stretch=False)
        tree.heading("Action", text="Action")
        tree.column("Action", width=128, stretch=False)

        tree.pack(side="left", expand=True, fill="both")
        scroll.pack(side="right", fill="y")

        self.file_tree = tree
        self.fr_file_list = frame

    def display_actions(self, master):
        def proceed_command():
            options = {
                "noBackup": self.noBackup.get(),
                "skipMonoize": self.skipMonoize.get(),
                "skipRemove": self.skipRemove.get(),
            }
            self._FileList.update_options(options)
            self._FileList.proceed()
            self.stage(0)

        def backup_command():
            # self.noBackup.set(False)
            print(self.noBackup.get())

        def skipMonoize_command(v):
            self.skipMonoize = v

        def skipRemove_command(v):
            self.skipRemove = v

        frame = ttk.Frame(master)
        top = ttk.Frame(frame)
        bottom = ttk.Frame(frame)
        self.bt_proceed = ttk.Button(bottom, text="Proceed", command=proceed_command)
        self.bt_proceed.pack(expand=True, fill="both")
        backup = ttk.Checkbutton(
            top,
            text="Back up to sub-folder: ",
            variable=self.noBackup,
            onvalue=False,
            offvalue=True,
            command=backup_command,
        )
        skipMonoize_button = ttk.Checkbutton(
            top,
            text="Skip Monoize",
            variable=self.skipMonoize,
            command=lambda: skipMonoize_command(self.skipMonoize.get()),
        )
        skipRemove_button = ttk.Checkbutton(
            top,
            text="Skip Monoize",
            variable=self.skipRemove,
            command=lambda: skipRemove_command(self.skipRemove.get()),
        )
        address = ttk.Entry(top, width=16)
        address.insert(0, self._FileList.options["backup"]["folder"])

        backup.pack(side="left", expand=False, fill="both")
        address.pack(side="left", expand=True, fill="x")
        skipMonoize_button.pack(side="left", expand=False, fill="both")
        skipRemove_button.pack(side="left", expand=False, fill="both")

        top.pack(expand=False, fill="x")
        bottom.pack(expand=True, fill="both", pady=16)

        self.fr_actions = frame
