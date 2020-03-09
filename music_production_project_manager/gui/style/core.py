from functools import wraps

import tkinter as tk
from tkinter import ttk

class Style:
    def __init__(self, data):
        self.data = data

    def _search(func):
        @wraps(func)
        def iterate(self, key, *args, delimiter=".", default="key", **kwargs):
            try:
                d = self.data[func.__name__]
                if delimiter in key:
                    for k in key.split(delimiter):
                        d = d[k]
                else:
                    d = key
                return func(self, d, *args, **kwargs)
            except KeyError:
                return key if default == "key" else default

        return iterate

    @_search
    def color(self, key):
        if isinstance(key, str):
            if key[0] == "#":
                return key
            d = self.data["color"]["theme"]
            if "_" in key:
                hue, level = key.split("_")
                return d[hue][int(level[:-1]) - 1]
            else:
                try:
                    return d[key]
                except (KeyError, IndexError):
                    return key
        return key

    @_search
    def typography(self, key, default=None):
        return key

    def fonttag(self, key):
        if key in ("p", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6"):
            return self.typography(f"tag.{key}")

    def fontface(self):
        return self.typography("fontface")

    def font(self, key):
        return (self.fontface(), self.fonttag(key)[1])



class BaseSetting:
    def __init__(self):
        self.settings = []

    def __call__(self, key, value):
        self.settings.append(key)
        setattr(self, key, value)

    def asdict(self):
        return {self.__class__.__name__.lower(): {k: getattr(self, k) for k in self.settings}}

class Configure(BaseSetting):
    pass



class Map(BaseSetting):
    def __call__(self, key, value, fixed=None, flex=None):
        flexmatrix = [(x, f"!{x}") for x in flex]
        states = [tuple(x) for x in flexmatrix]
        setattr(self, key, states)

class Settings:
    def __init__(self):
        self.widget_list = []
        self.widgets = {}
        pass

    def configure(self, key, **kw):
        conf = {k:v for k, v in kw}
        if key not in self.widget_list:
            self.widget_list.append(key)
            self.widgets[key] = {}
        self.widgets[key].update({"configure": conf})
