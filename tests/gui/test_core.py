import pytest
from music_production_project_manager.gui.style import core

# def test_search():
#     @core.search
#     def sample(data, key, *args, **kwargs):
#         pass
#     assert sample({"a": {"aa": 1}}, "a.aa", "arg") == 1
class ColorSample:
    def __init__(self):
        self.themes = self.setup_theme()
        self.properties = self.setup_properties()

    def setup_theme(self):
        themes = (
            "red",
            "magenta",
            "purple",
            "indigo",
            "blue",
            "sky",
            "teal",
            "green",
            "bronze",
            "slate",
            "dusk",
            "gray",
            "black",
            "white",
        )
        return {
            x: (
                f"#{x}"
                if x in ("black", "white")
                else [f"#{x}_{y + 1}0" for y in range(10)]
            )
            for x in themes
        }

    def setup_properties(self):
        return {
            "a": {"aa": "aaa", "ab": {"aba": "black"},},
            "b": {"ba": "gray_20", "bb": {"bba": "blue_10"}},
        }

    def asdict(self):
        color = {"theme": self.themes}
        color.update(self.properties)
        return {"color": color}


class TypographySample:
    def __init__(self):
        self.tag = self.setup_tag()

    def setup_tag(self):
        tags = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol")
        return {x: [f"style_{x}", f"size_{x}"] for x in tags}


color = ColorSample()
typography = TypographySample()


class TestStyle:
    def __init__(self):
        self.color = core.Style(color.asdict())
        self.typography = core.Style(typography.asdict())

    @pytest.mark.parametrize("key", ["black", "gray_100", "red_20",])
    def test_color_theme(self, key):
        assert self.color.color(key) == f"#{key}"

    @pytest.mark.parametrize(
        "key, value",
        [
            ("a.a", "aaa"),
            ("a.ab.aba", "#black"),
            ("b.ba", "#gray_20"),
            ("b.bb.bba", "#blue_10"),
        ],
    )
    def test_color_property(self, key, value):
        assert self.color.color(key) == value

    @pytest.mark.parametrize("key", ["#000", "Other"])
    def test_color_other(self, key):
        assert self.color.color(key) == key

    @pytest.mark.parametrize("key", ["h1", "h5", "p", "ol"])
    def test_typography(self, key):
        assert self.typography.typography(key) == [f"style_{key}", f"size_{key}"]

    @pytest.mark.parametrize("key", ["h2", "h3", "li"])
    def test_typography_font(self, key):
        assert self.typography.fonttag(key) == [f"style_{key}", f"size_{key}"]