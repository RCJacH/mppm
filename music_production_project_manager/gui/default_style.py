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
        self.setup_entry()
        self.setup_button()

    def setup_background(self):
        self.configure(
            ".", background=self.color("background.regular"), font=self.font("p"),
        )
        self.configure("border.TFrame", background=self.color("border.regular"))

    def setup_header(self):
        self.configure(
            "Header.TLabel",
            background=self.color("gray_100"),
            foreground=self.color("typography.inverted"),
            font=self.font("h1"),
            anchor="CENTER",
            padding=20,
            borderwidth=0,
        )

    def setup_label(self):
        self.configure(
            "TLabel",
            font=self.font("h4")
        )

    def setup_labelframe(self, inverted=False):
        k = "inverted" if inverted else "regular"
        self.configure(
            "TLabelFrame",
            background=self.color(f"background.panel.{k}"),
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
            padding=2,
            relief="flat",
        )

    def setup_button(self):
        self.configure(
            "TButton",
            font=self.font("h6"),
            anchor="CENTER",
            padding=[16, 4, 16, 4],
            borderwidth=1,
        )
        self.map(
            "TButton",
            background=[
                ("disabled", self.color("background.disabled")),
                ("!disabled", "readonly", self.color("background.active")),
                (
                    "!disabled",
                    "!readonly",
                    "!active",
                    self.color("background.action.regular"),
                ),
                (
                    "!disabled",
                    "!readonly",
                    "active",
                    self.color("background.action.hover"),
                ),
            ],
            foreground=[
                ("disabled", self.color("typography.disabled")),
                ("!disabled", "!active", self.color("typography.regular")),
                ("!disabled", "readonly", self.color("typography.readOnly")),
                ("active", self.color("typography.mouse")),
            ],
            relief=[
                ("disabled", "ridge"),
                ("!disabled", "ridge"),
                ("pressed", "!disabled", "sunken"),
            ],
        )

    def setup_checkbutton(self):
        self.configure(
            "TCheckbutton",
            font=self.font("p"),
            relief="flat",
        )
        self.map(
            "TCheckbutton",
        )