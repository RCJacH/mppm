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
def tmp_file(request, tmp_folder):
    testfile = get_audio_path(request.param)
    file = os.path.join(tmp_folder, os.path.split(testfile)[1])
    shutil.copyfile(testfile, file)
    yield (file, testfile)
    if os.path.isfile(file):
        os.remove(file)


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

    def test_backup(self):
        with AudioFile(get_audio_path("empty")) as obj:
            obj.backup()

    @pytest.mark.parametrize(
        "tmp_file, result", [("sin-s", True)], indirect=["tmp_file"]
    )
    def test_monolize(self, tmp_file, result):
        file, testfile = tmp_file
        with AudioFile(filename=file) as obj:
            obj.monolize()
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
        "tmp_file, result", [("empty", False)], indirect=["tmp_file"]
    )
    def test_remove(self, tmp_file, result):
        file, _ = tmp_file
        with AudioFile(filename=file) as obj:
            obj.remove(forced=True)
        assert os.path.isfile(file) == result
