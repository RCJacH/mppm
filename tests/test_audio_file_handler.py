"""
Tests for 'analyze' module
"""
import pytest
import os
import shutil
import numpy as np
from music_production_project_manager.audio_file_handler import AudioFile
from soundfile import SoundFile as sf
from soundfile import read


def get_audio_path(name, ext=".wav"):
    return os.path.join("tests", "audio_files", name + ext)


@pytest.fixture(scope="module", autouse=True)
def tmp_folder(tmp_path_factory):
    yield tmp_path_factory.mktemp("audio_temp_files")


@pytest.fixture(scope="function")
def tmp_file(request, tmp_path):
    try:
        filename = request.param
    except AttributeError:
        filename = "sin-m"
    testfile = get_audio_path(filename)
    file = os.path.join(tmp_path, os.path.split(testfile)[1])
    shutil.copyfile(testfile, file)
    yield (file, testfile)


class AudioInfo(object):
    def __init__(self, shape):
        self.shape = shape
        self.filename = get_audio_path(shape)
        self.src = AudioFile(self.filename)
        self.isCorrelated = False if ("+" in shape or "100" in shape) else True
        self.isEmpty = shape[0] == "0"
        self.isMono = False if (self.isEmpty or "+" in shape) else True
        self.channels = 1 if "-m" in shape else 2
        self.validChannel = (
            0 if "0-" in shape else 3 if "+" in shape else 2 if "r" in shape else 1
        )
        self.flag = (
            0 if self.isEmpty else 1 if "-m" in shape else 2 if "-r100" in shape else 3
        )
        self.isFakeStereo = self.isMono and self.channels == 2
        self.isMultichannel = shape[-1] == "n" or shape.count("+") > 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self.src


@pytest.fixture(
    params=["sin-m", "sin-s", "0-m", "0-s", "sin+tri", "sin-l50", "sin-r25", "sin-r100"]
)
def audioinfo(request):
    with AudioInfo(request.param) as info:
        yield info


class TestAudioFile:
    @pytest.fixture(
        params=[
            "flag",
            "isCorrelated",
            "validChannel",
            "channels",
            "isMono",
            "isEmpty",
            "isFakeStereo",
            "isMultichannel",
        ]
    )
    def each_attribute(self, request, audioinfo):
        yield [getattr(x, request.param) for x in (audioinfo.src, audioinfo)]

    def test_analyze(self, each_attribute):
        assert each_attribute[0] == each_attribute[1]

    def test_empty_file(self):
        with AudioFile(get_audio_path("empty")) as src:
            assert src.flag == None
            assert src.isCorrelated == None
            assert src.isMono == False
            assert src.isFakeStereo == False
            assert src.isMultichannel == False

    def test__enter__exit(self):
        with AudioFile(get_audio_path("empty")) as obj:
            assert obj.file is not None
            assert obj.channels == 1
        assert obj.file is None
        assert obj.channels == 1

    @pytest.mark.parametrize(
        "params, result",
        [
            pytest.param({}, ("bak", "sin-m.wav"), id="default"),
            pytest.param(
                {"folderExists": True}, ("bak1", "sin-m.wav"), id="inc-foldername"
            ),
            pytest.param(
                {"fileExists": True}, ("bak", "sin-m1.wav"), id="inc-filename"
            ),
            pytest.param(
                {"fileExists": True, "replace": True},
                ("bak", "sin-m.wav"),
                id="replace",
            ),
        ],
    )
    def test_backup(self, params, result, tmp_file):
        file, testfile = tmp_file
        filename = os.path.split(testfile)[1]
        tmppath = os.path.split(file)[0]
        bakpath = os.path.join(tmppath, "bak")
        if "folderExists" in params:
            os.makedirs(bakpath)
            bakpath += "1"
            params.pop("folderExists")
        if "fileExists" in params:
            os.makedirs(bakpath)
            with open(os.path.join(bakpath, filename), "w") as f:
                f.write("")
            params.pop("fileExists")
            params["newfolder"] = False
        with AudioFile(file) as obj:
            if "noAction" in params:
                assert obj.backup(**params) == result
            else:
                f = obj.backup(**params)
                newf = os.path.join(tmppath, *result)
                assert f == newf
                assert os.path.exists(newf)

    @pytest.mark.parametrize(
        "tmp_file, params, result",
        [
            ("sin-s", {}, True),
            ("sin+tri", {}, True),
            ("sin+tri", {"channel": 1}, False),
        ],
        indirect=["tmp_file"],
    )
    def test_monolize(self, tmp_file, params, result):
        file, testfile = tmp_file
        with AudioFile(filename=file) as obj:
            obj.monolize(**params)
            assert (
                np.all(
                    np.equal(
                        read(testfile, always_2d=True)[0],
                        list(obj.read(always_2d=True)),
                    )
                )
                == result
            )

    @pytest.mark.parametrize(
        "tmp_file, params, result",
        [("empty", {}, False), ("sin-m", {}, True), ("sin-m", {"forced": True}, False)],
        indirect=["tmp_file"],
    )
    def test_remove(self, tmp_file, params, result):
        file, _ = tmp_file
        with AudioFile(filename=file) as obj:
            obj.remove(**params)
        assert os.path.isfile(file) == result
