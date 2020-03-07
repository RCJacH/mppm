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
                return d[key]
        return key

    @_search
    def typography(self, key, default=None):
        return key

    def font(self, key):
        if key in ("p", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6"):
            return self.typography(f"tag.{key}")