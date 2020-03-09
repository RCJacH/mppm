import pytest
from music_production_project_manager.gui.style import core


class ColorSample:
    def __init__(self):
        self.themes = self.setup_theme()
        self.properties = self.setup_properties()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

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
        self.fontface = "fontface"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    def setup_tag(self):
        tags = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol")
        return {x: [f"style_{x}", f"size_{x}"] for x in tags}

    def asdict(self):
        typo = {"tag": self.tag, "fontface": self.fontface}
        return {"typography": typo}


@pytest.fixture(scope="module")
def color():
    with ColorSample() as o:
        yield core.Style(o.asdict())

@pytest.fixture(scope="module")
def typography():
    with TypographySample() as o:
        yield core.Style(o.asdict())


class TestStyle:
    @pytest.mark.parametrize("key", ["black", "gray_100", "red_20",])
    def test_color_theme(self, color, key):
        assert color.color(key) == f"#{key}"

    @pytest.mark.parametrize(
        "key, value",
        [
            ("a.aa", "aaa"),
            ("a.ab.aba", "#black"),
            ("b.ba", "#gray_20"),
            ("b.bb.bba", "#blue_10"),
        ],
    )
    def test_color_property(self, color, key, value):
        assert color.color(key) == value

    def test_color_property_not_found(self, color):
        assert color.color("a.a") == "a.a"

    def test_color_property_not_string(self, color):
        assert color.color(["a.a"]) == ["a.a"]

    @pytest.mark.parametrize("key", ["#000", "Other"])
    def test_color_other(self, color, key):
        assert color.color(key) == key

    @pytest.mark.parametrize("key", ["h1", "h5", "p", "ol"])
    def test_typography(self, typography, key):
        assert typography.typography(key) == key

    @pytest.mark.parametrize("key", ["h4", "h5", "ul"])
    def test_typography_fonttag(self, typography, key):
        assert typography.fonttag(key) == [f"style_{key}", f"size_{key}"]

    @pytest.mark.parametrize("key", ["h2", "h3", "li"])
    def test_typography_font(self, typography, key):
        assert typography.font(key) == (typography.fontface(), f"size_{key}")

    def test_typography_fontface(self, typography):
        assert typography.fontface() == "fontface"

class TestConfigure:

    def test_pass(self):
        pass