import tkinter as tk
import json
import os

from tkinter import ttk

from .style import core


class DefaultSetting(core.Settings, core.Style):
    def __init__(self):
        super().__init__()
        with open(
            os.path.join(os.path.dirname(__file__), "style", "mineral.json")
        ) as f:
            self.data = json.load(f)
        self.setup_background()
        self.setup_header()
        self.setup_labelframe()
        self.setup_label()
        self.setup_entry()
        self.setup_combobox()
        self.setup_button()
        self.setup_checkbutton()
        self.setup_scrollbar()
        self.setup_treeview()

    def setup_background(self):
        self.configure(
        ".", background=self.color("background.regular"), font=self.font("p"),
        )
        self.configure("border.TFrame", background=self.color("border.regular"))
        self.configure("TFrame", background=self.color("background.regular"))

    def setup_header(self):
        self.configure(
            "Header.TLabel",
            background=self.color("background.header"),
            foreground=self.color("typography.inverted"),
            font=self.font("h1"),
            anchor="CENTER",
            padding=20,
            borderwidth=0,
        )

    def setup_label(self):
        self.configure(
            "TLabel", background=self.color("background.regular"), font=self.font("h6")
        )

    def setup_labelframe(self, inverted=False):
        k = "inverted" if inverted else "regular"
        self.configure(
            "TLabelframe",
            background=self.color(f"background.{k}"),
            foreground=self.color(f"typography.{k}"),
            font=self.font("h4"),
            anchor="LEFT",
            padding=4,
            borderwidth=0,
        )

    def setup_entry(self):
        self.configure(
            "TEntry",
            background=self.color("input.background"),
            font=self.font("p"),
            padding=[4, 8] * 2,
            relief="flat",
        )

    def setup_combobox(self):
        self.configure(
            "TCombobox",
            background=self.color("input.background"),
            font=self.font("p"),
            padding=[4, 8] * 2,
            relief="flat",
        )

    def setup_button(self):
        self.configure(
            "TButton",
            font=self.font("h5"),
            anchor="CENTER",
            padding=[16, 4] * 2,
            borderwidth=1,
        )
        self.map(
            "TButton",
            background=[
                ("disabled", self.color("background.disabled")),
                (
                    "!disabled",
                    "!readonly",
                    "!active",
                    "!pressed",
                    "focus",
                    self.color("background.action.regular"),
                ),
                (
                    "!disabled",
                    "!readonly",
                    "!pressed",
                    "active",
                    self.color("background.action.hover"),
                ),
                (
                    "!disabled",
                    "!readonly",
                    "pressed",
                    self.color("background.action.pressed"),
                ),
                ("!disabled", "!focus", self.color("background.active")),
            ],
            foreground=[
                ("disabled", self.color("typography.disabled")),
                ("!disabled", "!active", self.color("typography.regular")),
                ("!disabled", "readonly", self.color("typography.readOnly")),
                ("active", self.color("typography.mouse")),
            ],
            relief=[
                ("disabled", "flat"),
                ("!pressed", "!disabled", "ridge"),
                ("pressed", "!disabled", "sunken"),
            ],
        )

    def setup_checkbutton(self):
        self.configure(
            "TCheckbutton",
            font=self.font("p"),
            relief="flat",
            background=self.color("background.regular"),
        )

    def setup_scrollbar(self):
        self.configure("TScrollbar", background=self.color("background.active"))

    def setup_treeview(self):
        self.configure(
            "Treeview",
            font=self.font("ol"),
            background=self.color("background.input"),
            fieldbackground=self.color("background.input"),
        )
        self.configure(
            "Treeview.Heading",
            background=self.color("background.well.regular"),
            font=self.font("h6"),
        )
        self.configure(
            "Treeview.Tag",
            font=self.font("ol"),
            background=self.color("background.input"),
        )
