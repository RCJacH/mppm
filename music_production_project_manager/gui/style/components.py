import json
import os
import tkinter as tk
from tkinter import ttk


class Box(ttk.Frame):
    def __init__(self, master=None, **kw):
        cursor = kw.pop("cursor", "")
        font = kw.pop("font", "Helvetica")
        class_ = kw.pop("class_", "Box")
        name = kw.pop("name", None)
        ttk.Frame.__init__(self, master, class_=class_, cursor=cursor, name=name)

        marginClass = kw.pop("marginClass", None)
        self.margin = ttk.Frame(
            self,
            style=f"{marginClass + '.' if marginClass else ''}margin.TFrame",
            padding=kw.pop("margin", 0),
        )
        borderClass = kw.pop("borderClass", None)
        self.border = ttk.Frame(
            self.margin,
            style=f"{borderClass + '.' if borderClass else ''}border.TFrame",
            padding=kw.pop("border", 0),
        )
        paddingClass = kw.pop("paddingClass", None)
        self.padding = ttk.Frame(
            self.border,
            style=f"{paddingClass + '.' if paddingClass else ''}padding.TFrame",
            padding=kw.pop("padding", 0),
        )

        self.fill = kw.pop("fill", "both")
        self.expand = kw.pop("expand", True)
        if not kw.pop("noMargin", False):
            self.margin.pack(fill=self.fill, expand=self.expand)
        if not kw.pop("noBorder", False):
            self.border.pack(fill=self.fill, expand=self.expand)
        if not kw.pop("noPadding", False):
            self.padding.pack(fill=self.fill, expand=self.expand)

        self.kw = kw


class Label(Box):
    def __init__(self, master=None, **kw):
        style = kw.pop("style", "")

        super().__init__(master=master, **kw)

        self.content = ttk.Label(
            self.padding, style=f"{style + '.' if style else ''}TLabel", **self.kw,
        )
        self.content.pack(fill=self.fill, expand=self.expand)


class Button(Box):
    def __init__(self, master=None, **kw):
        style = kw.pop("style", "")

        super().__init__(master=master, **kw)

        self.content = ttk.Button(
            self.padding, style=f"{style + '.' if style else ''}TButton", **self.kw,
        )
        self.content.pack(fill=self.fill, expand=self.expand)

    def invoke(self):
        """Invokes the command associated with the button."""
        return self.content.tk.call(self.content._w, "invoke")

