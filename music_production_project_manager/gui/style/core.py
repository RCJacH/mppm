from functools import wraps

import tkinter as tk
from tkinter import ttk


class Style:
    def __init__(self, data):
        self.data = data

    def _search(func):
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
    def __init__(self, settings=None):
        self.settings = []
        if settings is not None:
            for k in settings:
                self[k] = settings[k]

    def __call__(self, key=None, value=None):
        if key:
            k = str(key)
            if value:
                self[k] = value
            return self[k]
        else:
            return self.asdict()

    def __contains__(self, key):
        return str(key) in self.settings

    def __len__(self):
        return len(self.settings)

    def __getitem__(self, key):
        return getattr(self, str(key))

    def __setitem__(self, key, value):
        if key not in self:
            self.settings.append(key)
        setattr(self, key, value)

    def asdict(self):
        if len(self):
            return {
                self.__class__.__name__.lower(): {
                    k: self[k] for k in self.settings
                }
            }


class Configure(BaseSetting):
    pass


class Map(BaseSetting):
    def __call__(self, key=None, value=None, fixed=None, flex=None):
        v = value
        if fixed or flex:
            if flex:
                flexmatrix = [[x, f"!{x}"] for x in flex]
                r = [[]]
                for x in flexmatrix:
                    r = [i + [y] for y in x for i in r]
                states = [
                    tuple(
                        sorted((fixed or []) + x, key=lambda x: x.replace("!", ""))
                        + [v]
                    )
                    for x in r
                ]
            else:
                states = [tuple(sorted(fixed) + [v])]
            v = states
        return super().__call__(key, v)

class WidgetSetting:
    def __init__(self, settings=None):
        if not settings:
            settings = {}
        self.configure = Configure(settings=settings.pop("configure", None))
        self.map = Map(settings=settings.pop("map", None))

    def __call__(self):
        d = {}
        if self.configure():
            d.update(self.configure())
        if self.map():
            d.update(self.map())
        return d

    def set_configure(self, key, value):
        self.configure(key, value)

    def set_map(self, key, value, **kw):
        self.map(key, value, **kw)

class Settings:
    def __init__(self, settings):
        self.widgets = {}
        if settings:
            for w in settings:
                v = settings[w]
                if "configure" in v:
                    self.configure(w, **v["configure"])
                if "map" in v:
                    self.map(w, **v["map"])

    def __call__(self):
        return {str(w): self.widgets[w]() for w in self.widgets}

    def __contains__(self, key):
        return key in self.widgets

    def __getitem__(self, key):
        return self.widgets[str(key)]()

    def __len__(self):
        return len(self.widgets)

    def new(self, key):
        if key not in self.widgets:
            self.widgets[key] = WidgetSetting()

    def configure(self, key, **kw):
        self.new(key)
        for k in kw:
            self.widgets[key].set_configure(k, kw[k])

    def map(self, key, **kw):
        self.new(key)
        for k in kw:
            self.widgets[key].set_map(k, kw[k])
