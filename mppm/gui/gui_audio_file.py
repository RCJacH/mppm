import os
import string
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


from mppm import FileList
from .style import core
from .style import components
from .default_style import DefaultSetting

import logging

logger = logging.getLogger(__name__)


_valid_path_chars = frozenset(f"-_.() {string.ascii_letters}{string.digits}")


class FolderBrowser:
    def __init__(self, master=None, *args, **kwargs):
        # super().__init__(master, *args, **kwargs)
        self._FileList = FileList()
        self.master = master
        master.title("Music Production Project Manager")

        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True, fill="both")
        self.path = tk.StringVar()
        self.null_threshold = tk.DoubleVar()
        self.null_threshold.set(-100)
        self.empty_threshold = tk.DoubleVar()
        self.empty_threshold.set(-100)
        self.noBackup = tk.BooleanVar()
        self.keepMonoize = tk.BooleanVar()
        self.keepMonoize.set(True)
        self.keepRemove = tk.BooleanVar()
        self.keepRemove.set(True)
        self.keepJoin = tk.BooleanVar()
        self.keepJoin.set(True)
        self.backupPath = tk.StringVar()
        self.backupPath.set(self._FileList.options["backup_folder"])

        self.current_stage = tk.IntVar()
        self.analyzed = tk.BooleanVar()
        self.setup_style(self.master)

        top = ttk.Frame(self.frame, style="outline.TFrame")
        self.setup_header(top)
        self.setup_folder_selection(top)
        self.setup_input(top)
        self.fr_header.pack(anchor="n", expand=True, fill="x")
        self.fr_folder_selection.pack(anchor="n", expand=False, fill="x", padx=16)
        self.fr_input.pack(anchor="n", expand=False, fill="x", padx=16)
        top.pack(anchor="n", fill="x", ipady=8)

        mid = ttk.Frame(self.frame, style="outline.TFrame")
        self.display_file_list(mid)
        self.fr_file_list.pack(anchor="n", expand=True, fill="both", padx=16)
        mid.pack(anchor="n", expand=True, fill="both")

        bottom = ttk.Frame(self.frame, style="outline.TFrame")
        self.display_actions(bottom)
        self.fr_actions.pack(
            side="bottom", expand=False, fill="x", pady=[0, 16], padx=16
        )
        bottom.pack(anchor="n", fill="x")

        self.stage()
        # elif self.current_stage.get() > 1:

    def setup_style(self, master):
        s = ttk.Style()
        s.theme_create("Mineral", parent="clam", settings=DefaultSetting()())
        s.theme_use("Mineral")

    def stage(self, value=None):
        if value is not None:
            self.current_stage.set(value)
        stage = self.current_stage.get()
        if stage == 0:
            self.bt_browse.state(["!disabled", "focus"])
            self.bt_analyze.state(["disabled", "!focus"])
            self.bt_proceed.state(["disabled", "!focus"])
        elif stage == 1:
            self.bt_browse.state(["!disabled", "!focus"])
            self.bt_analyze.state(["!disabled", "focus"])
            self.bt_proceed.state(["disabled", "!focus"])
        elif stage == 2:
            self.bt_browse.state(["!disabled", "!focus"])
            self.bt_analyze.state(["readonly", "!focus"])
            self.bt_proceed.state(["!disabled", "focus"])
        elif stage == -1:
            self.bt_browse.state(["disabled", "!focus"])
            self.bt_analyze.state(["disabled", "!focus"])
            self.bt_proceed.state(["disabled", "!focus"])

    def setup_header(self, master):
        frame = ttk.Frame(master)
        title = ttk.Label(frame, text="Project Audio Files", style="Header.TLabel")
        title.pack(expand=True, fill="x")
        self.fr_header = frame

    def setup_folder_selection(self, master):
        frame = ttk.Frame(master)
        address_label = ttk.Label(frame, text="Select Folder:", style="Panel.TLabel")
        address_label.pack(side="left")
        addressCmd = (master.register(self.address_validation), "%P")
        self.address = ttk.Entry(frame, validate="key", validatecommand=addressCmd)
        self.address.pack(side="left", expand=True, fill="x", padx=8)
        self.bt_browse = ttk.Button(frame, text="Browse", command=self.browse_command)
        self.bt_browse.pack(side="left", expand=False)

        self.fr_folder_selection = frame

    def browse_command(self):
        path = tk.filedialog.askdirectory(initialdir=self.path.get())
        if path and os.path.exists(path):
            self.path.set(path)
            self.address.delete(0, tk.END)
            self.address.insert(0, path)
            self.stage(1)

    def address_validation(self, path):
        if path == self.path.get():
            if self.analyzed.get():
                self.stage(2)
            else:
                self.stage(1)
            return True
        else:
            if os.path.exists(path):
                self.path.set(path)
                self.stage(1)
            else:
                self.stage(0)
            return True

    def setup_input(self, master):
        frame = ttk.Frame(master)
        top = ttk.Frame(frame)
        mid = ttk.Frame(frame)
        bottom = ttk.Frame(frame)

        lb_blocksize = ttk.Label(None, text="Blocksize", padding=[8, 0] * 2)
        blocksize = ttk.LabelFrame(
            top,
            labelwidget=lb_blocksize,
            text="Blocksize",
            labelanchor="n",
            borderwidth=1,
            padding=[8, 8, 8, 16],
            relief="sunken",
        )
        cb_blocksize = ttk.Combobox(
            blocksize,
            justify="center",
            values=["None", 24000, 44100, 48000, 88200, 96000, 176400, 192000, 384000],
        )
        cb_blocksize.set("None")
        cb_blocksize.pack(side="bottom")
        self.blocksize = cb_blocksize

        lb_null_threshold = ttk.Label(None, text="Null threshold", padding=[8, 0] * 2)
        null_threshold = ttk.LabelFrame(
            top,
            labelwidget=lb_null_threshold,
            text="Null threshold",
            labelanchor="n",
            borderwidth=1,
            padding=[8, 8, 8, 16],
            relief="sunken",
        )
        en_null_threshold = ttk.Entry(
            null_threshold,
            justify="center",
            validate="key",
            validatecommand=(master.register(self.null_validation), "%P"),
        )
        en_null_threshold.insert(
            0, "{:.20f}".format(self.null_threshold.get()).rstrip("0")
        )
        en_null_threshold.pack(side="bottom")

        lb_empty_threshold = ttk.Label(None, text="Empty threshold", padding=[8, 0] * 2)
        empty_threshold = ttk.LabelFrame(
            top,
            labelwidget=lb_empty_threshold,
            text="Empty threshold",
            labelanchor="n",
            borderwidth=1,
            padding=[8, 8, 8, 16],
            relief="sunken",
        )
        en_empty_threshold = ttk.Entry(
            empty_threshold,
            justify="center",
            validate="key",
            validatecommand=(master.register(self.empty_validation), "%P"),
        )
        en_empty_threshold.insert(
            0, "{:.20f}".format(self.empty_threshold.get()).rstrip("0")
        )
        en_empty_threshold.pack(side="bottom")

        lb_actions = ttk.Label(None, text="Actions", padding=[8, 0] * 2)
        actions = ttk.LabelFrame(
            mid,
            labelwidget=lb_actions,
            text="Actions",
            labelanchor="n",
            borderwidth=1,
            padding=[8, 8, 8, 16],
            relief="sunken",
        )
        keepMonoize_button = ttk.Checkbutton(
            actions,
            text="Monoize",
            variable=self.keepMonoize,
            command=self.analyze_command,
        )
        keepRemove_button = ttk.Checkbutton(
            actions,
            text="Remove",
            variable=self.keepRemove,
            command=self.analyze_command,
        )
        keepJoin_button = ttk.Checkbutton(
            actions, text="Join", variable=self.keepJoin, command=self.analyze_command
        )

        keepMonoize_button.pack(side="left", expand=True)
        keepRemove_button.pack(side="left", expand=True)
        keepJoin_button.pack(side="left", expand=True)

        self.bt_analyze = ttk.Button(
            bottom, text="Analyze", command=self.analyze_command
        )

        self.bt_analyze.pack(side="left", expand=True, fill="x")
        blocksize.pack(side="left", expand=True, fill="x", padx=[0, 4])
        null_threshold.pack(side="left", expand=True, fill="x", padx=[4, 4])
        empty_threshold.pack(side="left", expand=True, fill="x", padx=[4, 0])
        actions.pack(side="left", expand=True, fill="x")
        top.pack(expand=True, fill="x")
        mid.pack(expand=True, fill="x", pady=8)
        bottom.pack(expand=True, fill="x", pady=8)

        self.fr_input = frame

    def null_validation(self, P):
        try:
            self.null_threshold.set(float(-300 if not P or P == "-" else P))
            return True
        except ValueError:
            return False

    def empty_validation(self, P):
        try:
            self.empty_threshold.set(float(-300 if not P or P == "-" else P))
            return True
        except ValueError:
            return False

    def update_filelist(self):
        options = {
            "null_threshold": self.null_threshold.get(),
            "empty_threshold": self.empty_threshold.get(),
            "blocksize": self.blocksize.get(),
            "monoize": self.keepMonoize.get(),
            "remove": self.keepRemove.get(),
            "join": self.keepJoin.get(),
        }
        self._FileList.folderpath = self.path.get()
        self._FileList.update_options(options)
        self._FileList.set_default_action()

    def analyze_command(self):
        def check(v):
            return "x" if v else ""

        def select(f):
            return f.action

        if not os.path.exists(self.path.get()):
            self.stage(0)
            return

        self.stage(-1)
        self.update_filelist()
        self.file_tree.delete(*self.file_tree.get_children())
        for file in self._FileList:
            self.file_tree.insert(
                "",
                "end",
                text=file.basename,
                values=[
                    file.channels,
                    check(file.isEmpty),
                    check(file.isMono),
                    check(file.isFakeStereo),
                    check(file.isStereo),
                    check(file.isMultichannel),
                    select(file),
                ],
            )
        self.analyzed.set(True)
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
        tree.column("#1", width=96, stretch=False, anchor="n")
        tree.heading("Empty", text="Empty")
        tree.column("Empty", width=x_width, stretch=False, anchor="n")
        tree.heading("Mono", text="Mono")
        tree.column("Mono", width=x_width, stretch=False, anchor="n")
        tree.heading("Fake", text="Fake")
        tree.column("Fake", width=x_width, stretch=False, anchor="n")
        tree.heading("Stereo", text="Stereo")
        tree.column("Stereo", width=x_width, stretch=False, anchor="n")
        tree.heading("Multi", text="Multi")
        tree.column("Multi", width=x_width, stretch=False, anchor="n")
        tree.heading("Action", text="Action")
        tree.column("Action", width=128, stretch=False, anchor="n")

        tree.pack(side="left", expand=True, fill="both")
        scroll.pack(side="right", fill="y")

        self.file_tree = tree
        self.fr_file_list = frame

    def display_actions(self, master):
        frame = ttk.Frame(master)
        top = ttk.Frame(frame)
        bottom = ttk.Frame(frame)
        self.bt_proceed = ttk.Button(
            bottom, text="Proceed", command=self.proceed_command
        )
        self.bt_proceed.pack(expand=True, fill="both")
        backup = ttk.Frame(top)
        lb_backup = ttk.Checkbutton(
            backup,
            text="Back up to sub-folder: ",
            variable=self.noBackup,
            onvalue=False,
            offvalue=True,
        )
        address = ttk.Entry(
            backup,
            width=16,
            textvariable=self.backupPath,
            validate="key",
            validatecommand=(master.register(self.path_validation), "%S"),
        )

        lb_backup.pack(side="left", expand=False)
        address.pack(side="left", expand=True, fill="x", padx=8)
        backup.pack(side="left", expand=True)

        top.pack(expand=False, fill="x", pady=16)
        bottom.pack(expand=True, fill="both")

        self.fr_actions = frame

    def path_validation(self, S):
        return S in _valid_path_chars

    def proceed_command(self):
        options = {
            "noBackup": self.noBackup.get(),
            "monoize": self.keepMonoize.get(),
            "remove": self.keepRemove.get(),
        }
        self._FileList.update_options(options)
        self._FileList.proceed()
        self.analyze_command()
        self.stage(0)
