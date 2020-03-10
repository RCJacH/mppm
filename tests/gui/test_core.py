import pytest
from music_production_project_manager.gui.style import core


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
        self.fontface = "fontface"

    def setup_tag(self):
        tags = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol")
        return {x: [f"style_{x}", f"size_{x}"] for x in tags}

    def asdict(self):
        typo = {"tag": self.tag, "fontface": self.fontface}
        return {"typography": typo}


@pytest.fixture(scope="module")
def color():
    return core.Style(ColorSample().asdict())


@pytest.fixture(scope="module")
def typography():
    return core.Style(TypographySample().asdict())


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
    @pytest.fixture(scope="function")
    def configure(self):
        yield core.Configure

    @pytest.mark.parametrize(
        "settings", [(None), ({"background": "#FFF", "foreground": "#000"}),]
    )
    def test__init__len__(self, configure, settings):
        obj = configure(settings)
        assert isinstance(obj.settings, list)
        if settings:
            assert len(obj) == len(settings)
            assert all(obj[k] == settings[k] for k in settings)
        else:
            assert not len(obj)

    @pytest.mark.parametrize("key, value", [("bg", "#FFF"), ("padding", [1, 2, 3, 4])])
    def test__call__contains__(self, configure, key, value):
        obj = configure()
        obj(key, value)
        assert key in obj
        assert obj[key] == value

    def test__call__key_only(self, configure):
        obj = configure()
        obj("k", "v")
        assert obj("k") == "v"

    def test__call__no_input(self, configure):
        obj = configure()
        obj("k", "v")
        assert obj() == {"configure": {"k": "v"}}

    def test_asdict(self, configure):
        obj = configure()
        obj("a", "aa")
        obj("b", "bb")
        assert obj.asdict() == {"configure": {"b": "bb", "a": "aa"}}


class TestMap:
    @pytest.fixture(scope="function")
    def settingmap(self):
        yield core.Map

    @pytest.mark.parametrize(
        "key, value, kwarg, result",
        [
            pytest.param("bg", "v", {"fixed": ["d"]}, [("d", "v")], id="single_fixed",),
            pytest.param(
                "bg", "v", {"fixed": ["d", "a"]}, [("a", "d", "v")], id="multi_fixed",
            ),
            pytest.param(
                "bg", "v", {"flex": ["d"]}, [("d", "v"), ("!d", "v")], id="single_flex"
            ),
            pytest.param(
                "bg",
                "v",
                {"flex": ["d", "a"]},
                [
                    ("a", "d", "v"),
                    ("!a", "d", "v"),
                    ("a", "!d", "v"),
                    ("!a", "!d", "v"),
                ],
                id="multi_flex",
            ),
            pytest.param(
                "bg",
                "v",
                {"fixed": ["f", "i"], "flex": ["d", "a"]},
                [
                    ("a", "d", "f", "i", "v"),
                    ("!a", "d", "f", "i", "v"),
                    ("a", "!d", "f", "i", "v"),
                    ("!a", "!d", "f", "i", "v"),
                ],
                id="multi_all",
            ),
        ],
    )
    def test__call__(self, settingmap, key, value, kwarg, result):
        obj = settingmap()
        obj(key, value, **kwarg)
        assert sorted(obj[key]) == sorted(result)

    def test__call__no_input(self, settingmap):
        init = {"bd": [("a", "d", "v")]}
        obj = settingmap(init)
        assert obj() == {"map": init}

class TestSettings:
    @pytest.fixture("function")
    def settings(self):
        yield core.Settings

    def test__init__len__(self, settings):
        init = {
            "TLabel": {"configure": {"bg": "v"}},
            "TButton": {"map": {"bd": [("a", "d", "v")]}},
        }
        obj = settings(init)
        assert len(obj) == len(init)
        assert all(k in obj for k in init)
        # print(obj["TLabel"], obj["TButton"])
        assert all(obj[k] == init[k] for k in init)

    def test__init__len__None(self, settings):
        obj = settings(None)
        assert not len(obj)

    def test__call__(self, settings):
        init = {
            "W": {"configure": {"k": "v"}},
            "W2": {"map": {"k2": [("a", "d", "v2")]}},
        }
        obj = settings(init)
        assert obj() == init
